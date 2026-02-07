 # 🤖 Gemini Stock Chatbot 📈

Witaj w Gemini Stock Chatbot! Ta aplikacja SPA (Single Page Application) pozwala na analizę wykresów giełdowych za pomocą sztucznej inteligencji Google Gemini. Po prostu prześlij zdjęcie wykresu, albo zapytaj o dany ticker, a nasz bot dostarczy Ci informacji o trendach i poradzi, czy warto inwestować!

## ✨ Funkcje

*   **Analiza Wykresów Giełdowych:** Prześlij zdjęcie wykresu, a Gemini Pro zajmie się resztą.
*   **Porady Inwestycyjne:** Otrzymuj informacje o trendach, poziomach wsparcia/oporu oraz rekomendacje (kupuj/sprzedawaj/trzymaj).
*   **Czat Intuicyjny:** Łatwy w użyciu interfejs czatu do interakcji z botem.
*   **Tryb Jasny/Ciemny:** Nowoczesne stylowanie z możliwością przełączania trybu wyświetlania.
*   **Bezpieczne API Key:** Twój klucz API Google Gemini jest przechowywany tylko lokalnie w Twojej sesji przeglądarki.

## 🚀 Jak Uruchomić Aplikację

Ta aplikacja składa się z dwóch części: backendu (FastAPI) i frontendu (React). Aby ją uruchomić, musisz uruchomić obie te części.

### 🐍 Uruchamianie Backendu (FastAPI)

1.  **Wymagania:** Upewnij się, że masz zainstalowanego Pythona (zalecane 3.8+) oraz `pip`.

2.  **Instalacja Zależności:**
    Otwórz terminal w **głównym katalogu projektu** (tam gdzie znajduje się `backend_app.py`) i zainstaluj niezbędne pakiety Pythona:

    ```bash
    pip install fastapi uvicorn google-generativeai python-multipart Pillow
    ```

3.  **Uruchamianie Serwera:**
    Po zainstalowaniu pakietów, uruchom serwer FastAPI:

    ```bash
    uvicorn backend_app:app --reload
    ```
    ✅ Backend będzie dostępny pod adresem: `http://127.0.0.1:8000`

### ⚛️ Uruchamianie Frontendu (React)

1.  **Wymagania:** Upewnij się, że masz zainstalowanego Node.js (zalecane 14+) oraz `npm`.

2.  **Przejdź do Katalogu Frontendu:**
    Otwórz **nowy terminal lub wiersz poleceń** i przejdź do katalogu `frontend`:

    ```bash
    cd frontend
    ```

3.  **Instalacja Zależności:**
    Zainstaluj zależności Node.js:

    ```bash
    npm install
    ```

4.  **Uruchamianie Aplikacji:**
    Uruchom serwer deweloperski React:

    ```bash
    npm start
    ```
    🚀 Aplikacja frontendowa otworzy się automatycznie w Twojej przeglądarce pod adresem: `http://localhost:3000`

## 👨‍💻 Jak Korzystać z Aplikacji

1.  **Otwórz Aplikację:** Upewnij się, że zarówno backend FastAPI, jak i frontend React są uruchomione. Otwórz przeglądarkę i przejdź do `http://localhost:3000`.

2.  **Podaj Klucz API Gemini:**
    Na stronie głównej znajdziesz pole do wprowadzenia Twojego klucza API Google Gemini. Jest to niezbędne, aby aplikacja mogła komunikować się z modelem AI. Klucz API możesz wygenerować na [Google AI Studio](https://aistudio.google.com/app/apikey).
    🔑 *Pamiętaj: Twój klucz API jest używany tylko po stronie klienta i nie jest nigdzie przechowywany ani wysyłany do backendu.*

3.  **Zadaj Pytanie lub Prześlij Wykres:**
    *   Wpisz swoje pytanie dotyczące wykresu giełdowego w polu tekstowym.
    *   Użyj przycisku "Wybierz plik", aby przesłać zdjęcie wykresu, który chcesz analizować.
    *   Kliknij przycisk "Send" (Wyślij).

4.  **Otrzymaj Odpowiedź:**
    Bot Gemini przetworzy Twoje zapytanie i obraz, a następnie wyświetli analizę i rekomendację w oknie czatu.

## 🎨 Stylowanie

Aplikacja posiada nowoczesne stylowanie z możliwością przełączania trybu jasnego i ciemnego. Przycisk do zmiany trybu znajdziesz w nagłówku aplikacji.

---

Ciesz się korzystaniem z Gemini Stock Chatbot! Wszelkie uwagi i propozycje ulepszeń są mile widziane. 😊
