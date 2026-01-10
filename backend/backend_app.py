import json
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
import chromadb

#SDK Google GenAI
import google.genai as genai
from google.genai import types

from tools import *

app = FastAPI()

# Konfiguracja
ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]

chroma_client = chromadb.PersistentClient(path="./chroma_db")
rag_collection = chroma_client.get_or_create_collection(name="finance_knowledge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def generate_response_stream(
    client: genai.Client,
    model_id: str,
    user_parts: list,
    history: list,
    tools_config: list,
    system_instruction: str
) -> AsyncGenerator[str, None]:
    """Obsługuje pętlę konwersacji z Function Calling przy użyciu SDK genai."""
    try:
        chat = client.chats.create(
            model=model_id,
            config=types.GenerateContentConfig(
                tools=tools_config,
                system_instruction=system_instruction
            ),
            history=history
        )

        current_input = user_parts

        while True:
            # SDK genai wysyła żądanie
            response = await asyncio.to_thread(chat.send_message, message=current_input)
            
            if not response.candidates or not response.candidates[0].content.parts:
                yield "Błąd: Brak treści w odpowiedzi modelu."
                break

            part = response.candidates[0].content.parts[0]

            # Obsługa Function Call
            if part.function_call:
                fn = part.function_call
                log_to_file(f"Model wywołuje: {fn.name} z {fn.args}")
                
                try:
                    # Wykonanie żądania do mostka MCP
                    result_text = await call_mcp_tool_http(fn.name, dict(fn.args))
                    log_to_file(f"Wynik MCP: {result_text}")

                    # Przygotowanie odpowiedzi funkcji dla modelu
                    current_input = types.Part.from_function_response(
                        name=fn.name,
                        response={"result": result_text}
                    )
                except Exception as e:
                    log_to_file(f"Błąd wywołania narzędzia: {str(e)}")
                continue # Wraca do modelu z wynikami
            
            # Jeśli model zwrócił tekst
            if part.text:
                log_to_file(f"AI: {part.text}")
                yield part.text
            break

    except Exception as e:
        log_to_file(f"Błąd strumieniowania: {str(e)}")
        yield f"Wystąpił błąd: {str(e)}"

@app.post("/ingest")
async def ingest_knowledge(
    text: str = Form(...),
    x_gemini_api_key: str = Header(...)
):
    """Dodaje tekst do bazy wiedzy RAG."""
    try:
        client = genai.Client(api_key=x_gemini_api_key)
        # Generowanie embeddingu dla tekstu
        resp = await asyncio.to_thread(
            client.models.embed_content,
            model="text-embedding-004",
            contents=text
        )
        
        embedding = resp.embeddings[0].values

        rag_collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(datetime.now().timestamp())]
        )
        return {"status": "ok", "message": "Wiedza dodana do bazy."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(
    file: Optional[UploadFile] = File(None),
    message: str = Form(""),
    history: str = Form("[]"),
    model_name: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None)
):
    if not x_gemini_api_key:
        raise HTTPException(status_code=400, detail="Nagłówek X-Gemini-Api-Key jest wymagany.")

    client = genai.Client(api_key=x_gemini_api_key)
    selected_model = model_name if model_name in ALLOWED_MODELS else "gemini-2.5-flash"

    # Pobieranie narzędzi (dynamicznie przy każdym zapytaniu lub można zcache'ować)
    declarations = await get_mcp_tools_http()
    tools_config = [types.Tool(function_declarations=declarations)] if declarations else None

    # Historia
    formatted_history = []
    try:
        raw_history = json.loads(history)
        for h in raw_history:
            role = "user" if h.get("role") == "user" else "model"
            formatted_history.append(types.Content(role=role, parts=[types.Part(text=h.get("text", ""))]))
    except:
        pass

    # Części wiadomości użytkownika
    user_parts = []
    rag_context = ""

    if message:
        user_parts.append(types.Part(text=message))
        log_to_file(f"User: {message}")

        # --- LOGIKA RAG ---
        try:
            # 1. Zamiana pytania użytkownika na wektor
            emb_resp = await asyncio.to_thread(
                client.models.embed_content,
                model="text-embedding-004",
                contents=message
            )
            embedding = emb_resp.embeddings[0].values
            print(embedding)
            
            # 2. Wyszukanie w bazie
            results = rag_collection.query(
                query_embeddings=[embedding],
                n_results=3 
            )
            if results["documents"] and results["documents"][0]:
                rag_context = "\n".join(results["documents"][0])
                log_to_file(f"Znaleziono kontekst RAG: {rag_context[:100]}...")
        except Exception as e:
            log_to_file(f"Błąd RAG: {e}")
        # ------------------

    if file and "image" in file.content_type:
        img_data = await file.read()
        user_parts.append(types.Part.from_bytes(data=img_data, mime_type=file.content_type))

    base_instruction = "Jesteś ekspertem finansowym. Używaj narzędzi do pobierania danych giełdowych. Przedstawiaj sugestie oraz przewidywania przyszłościowe dla kursów. Sugeruj co moze byc dobre do inwestowania."
    if rag_context:
        base_instruction += f"\n\nOto dodatkowe informacje z bazy wiedzy, które mogą być pomocne:\n{rag_context}\nUżyj ich, jeśli są relewantne do pytania."

    return StreamingResponse(
        generate_response_stream(
            client, 
            selected_model, 
            user_parts, 
            formatted_history, 
            tools_config, 
            base_instruction),
        media_type="text/plain"
    )

@app.get("/")
async def root():
    return {"status": "running", "engine": "google-genai", "mcp_mode": "http-bridge"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)