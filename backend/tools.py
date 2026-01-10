import json
import httpx
from datetime import datetime

from google.genai import types


LOG_FILE = "log.txt"
MCP_URL = "https://mcp.alphavantage.co/mcp"
ALPHA_VANTAGE_API_KEY = "6F7QZGBQOEMUB3RE"

def log_to_file(text: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

async def get_mcp_tools_http() -> list:
    """Pobiera listę narzędzi z serwera MCP przez JSON-RPC nad HTTP."""
    payload = {
        "jsonrpc": "2.0",
        "id": "list-tools-1",
        "method": "tools/list",
        "params": {}
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_URL}?apikey={ALPHA_VANTAGE_API_KEY}",
                json=payload,
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                mcp_tools = data.get("result", {}).get("tools", [])
                
                # Konwersja formatu MCP na FunctionDeclaration dla google-genai
                declarations = []
                for tool in mcp_tools:
                    declarations.append(
                        types.FunctionDeclaration(
                            name=tool["name"],
                            description=tool["description"],
                            parameters=tool["inputSchema"]
                        )
                    )
                return declarations
            return []
    except Exception as e:
        log_to_file(f"Błąd pobierania narzędzi: {e}")
        return []

async def call_mcp_tool_http(name: str, arguments: dict) -> str:
    """Wywołuje narzędzie na serwerze MCP przez JSON-RPC nad HTTP."""
    payload = {
        "jsonrpc": "2.0",
        "id": "call-tool-1",
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_URL}?apikey={ALPHA_VANTAGE_API_KEY}",
                json=payload,
                timeout=30.0
            )
            data = response.json()
            # Wyciągamy tekst z odpowiedzi MCP
            content = data.get("result", {}).get("content", [])
            if content and "text" in content[0]:
                return content[0]["text"]
            return json.dumps(data.get("result", {}))
    except Exception as e:
        return f"Error calling tool: {str(e)}"
