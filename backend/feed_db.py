import requests
import os
import yfinance as yf

# --- KONFIGURACJA ---
BACKEND_URL = "http://localhost:8000/ingest"
GEMINI_API_KEY = "AIzaSyAnS6RzoMd8TclFuEbpGF7xWO9j2rtFu3k"  # <-- WAŻNE: Podaj swój klucz
TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    "META": "Meta Platforms",
    "BRK.B": "Berkshire Hathaway",
    "JPM": "JPMorgan Chase",
    "V": "Visa",
    "WMT": "Walmart",
    "LLY": "Eli Lilly",
    "AVGO": "Broadcom",
    "TSM": "TSMC",
    "ORCL": "Oracle",
    "XOM": "Exxon Mobil",
    "JNJ": "Johnson & Johnson",
    "BAC": "Bank of America",
    "UNH": "UnitedHealth Group",
    "PG": "Procter & Gamble",
}

def send_to_rag(text):
    """Wysyła tekst do Twojego backendu."""
    if not text or len(text) < 10:
        return
    
    try:
        print(f"Wysyłanie: {text[:60]}...")
        response = requests.post(
            BACKEND_URL,
            headers={"x-gemini-api-key": GEMINI_API_KEY},
            data={"text": text}
        )
        if response.status_code == 200:
            print(" -> SUKCES")
        else:
            print(f" -> BŁĄD: {response.text}")
    except Exception as e:
        print(f" -> WYJĄTEK: {e}")

# --- METODA 1: Ręczna lista faktów ---
def feed_manual_data():
    print("\n--- Ładowanie danych ręcznych ---")
    facts = [
        "Spółka NVIDIA ogłosiła split akcji 10 na 1, który wejdzie w życie 7 czerwca 2024.",
        "Inflacja w strefie Euro spadła do 2.4% w kwietniu, co zwiększa szanse na obniżkę stóp procentowych.",
        "CD Projekt RED zapowiedział, że prace nad nowym Wiedźminem (Project Polaris) przyspieszają."
    ]
    for fact in facts:
        send_to_rag(fact)

# --- METODA 2: Pliki tekstowe z folderu 'wiedza' ---
def feed_from_files():
    folder_name = "wiedza"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"\n[INFO] Utworzono folder '{folder_name}'. Wrzuć tam pliki .txt i uruchom skrypt ponownie.")
        return

    print(f"\n--- Ładowanie plików z folderu '{folder_name}' ---")
    for filename in os.listdir(folder_name):
        if filename.endswith(".txt"):
            path = os.path.join(folder_name, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                send_to_rag(content)

# --- METODA 3: Newsy giełdowe z yfinance ---
def feed_from_yfinance(ticker_symbol):
    print(f"\n--- Pobieranie newsów dla {ticker_symbol} ---")
    ticker = yf.Ticker(ticker_symbol)
    news_list = ticker.news
    for item in news_list:
        content = item.get("content", {})
        title = content.get("title", "")
        summary = content.get("summary", "")
        description = content.get("description", "")
        rag_text = f"{title}\n\n{summary}\n\n{description}".strip()
        send_to_rag(rag_text)


if __name__ == "__main__":
    # Odkomentuj to, co chcesz uruchomić:
    # feed_manual_data()
    # feed_from_files()
    for ticker, company in TICKERS.items():
        feed_from_yfinance(ticker) 
