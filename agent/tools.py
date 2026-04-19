"""
agent/tools.py
Definicje narzędzi dla agenta (Anthropic tool_use schema).
Każde narzędzie ma: schemat JSON (dla API) + funkcję wykonującą.
"""

import math
import os
import httpx


# ---------------------------------------------------------------------------
# SCHEMATY NARZĘDZI – wysyłane do Claude API
# Claude sam decyduje które wywołać i z jakimi parametrami
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Oblicza wyrażenia matematyczne. Obsługuje: +, -, *, /, **, sqrt, sin, cos, "
            "log, pi, e. Używaj gdy użytkownik pyta o obliczenia."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Wyrażenie matematyczne, np. '2 ** 10' lub 'sqrt(144)'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": (
            "Pobiera aktualne dane pogodowe dla podanego miasta. "
            "Używa darmowego Open-Meteo API (nie wymaga klucza)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nazwa miasta, np. 'Warsaw', 'Krakow', 'London'",
                }
            },
            "required": ["city"],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Wyszukuje informacje w internecie. Używaj gdy pytanie dotyczy "
            "bieżących wydarzeń, faktów lub rzeczy których nie znasz."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Zapytanie do wyszukiwarki",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": (
            "Odczytuje zawartość lokalnego pliku tekstowego. "
            "Przydatne do analizy dokumentów, logów, plików CSV."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Ścieżka do pliku (względna lub absolutna)",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maksymalna liczba znaków do odczytania (domyślnie 3000)",
                    "default": 3000,
                },
            },
            "required": ["filepath"],
        },
    },
]


# ---------------------------------------------------------------------------
# IMPLEMENTACJE NARZĘDZI
# ---------------------------------------------------------------------------

def tool_calculator(expression: str) -> str:
    """
    Bezpieczny kalkulator – eval z ograniczonym namespace.
    Obsługuje: podstawowe operacje, potęgowanie, sqrt, trygonometrię, logarytmy.
    """
    # Dozwolone funkcje z modułu math + stałe
    safe_namespace = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "__builtins__": {},  # Wyłącz dostęp do wbudowanych funkcji Pythona
    }

    try:
        result = eval(expression, safe_namespace)  # noqa: S307
        return f"Wynik: {expression} = {result}"
    except ZeroDivisionError:
        return "Błąd: dzielenie przez zero"
    except Exception as exc:
        return f"Błąd obliczenia: {exc}"


def tool_get_weather(city: str) -> str:
    """
    Pobiera pogodę dla miasta z Open-Meteo (geocoding + weather API).
    Darmowe, nie wymaga klucza API.
    """
    try:
        # Krok 1: Geokodowanie – znajdź współrzędne miasta
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = httpx.get(geo_url, params={"name": city, "count": 1, "language": "pl"}, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return f"Nie znaleziono miasta: {city}"

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location.get("name", city)
        country = location.get("country", "")

        # Krok 2: Pobierz pogodę
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "wind_speed_unit": "kmh",
        }
        weather_resp = httpx.get(weather_url, params=params, timeout=10)
        weather = weather_resp.json()["current"]

        # Mapowanie kodu pogodowego na opis
        weather_codes = {
            0: "Bezchmurnie ☀️",
            1: "Głównie pogodnie 🌤️",
            2: "Częściowe zachmurzenie ⛅",
            3: "Zachmurzenie ☁️",
            45: "Mgła 🌫️",
            51: "Mżawka 🌦️",
            61: "Deszcz 🌧️",
            71: "Śnieg 🌨️",
            80: "Przelotne opady 🌦️",
            95: "Burza ⛈️",
        }
        code = weather.get("weather_code", 0)
        description = weather_codes.get(code, f"Kod pogodowy: {code}")

        return (
            f"Pogoda w {name}, {country}:\n"
            f"  Temperatura: {weather['temperature_2m']}°C\n"
            f"  Wilgotność: {weather['relative_humidity_2m']}%\n"
            f"  Wiatr: {weather['wind_speed_10m']} km/h\n"
            f"  Warunki: {description}"
        )
    except httpx.TimeoutException:
        return "Błąd: przekroczono czas oczekiwania na odpowiedź API pogodowego"
    except Exception as exc:
        return f"Błąd pobierania pogody: {exc}"


def tool_web_search(query: str) -> str:
    """
    Symulowana wyszukiwarka (mock).

    W produkcji: zastąp implementacją Serper.dev lub DuckDuckGo API:

        SERPER_API_KEY = os.getenv("SERPER_API_KEY")
        resp = httpx.post("https://google.serper.dev/search",
                          headers={"X-API-KEY": SERPER_API_KEY},
                          json={"q": query})
        results = resp.json()["organic"][:3]
        return "\n".join(f"- {r['title']}: {r['snippet']}" for r in results)
    """
    # Mock – zwraca informację że to symulacja
    return (
        f"[MOCK] Wyniki wyszukiwania dla: '{query}'\n"
        "Ta implementacja jest zaślepką (mock).\n"
        "Aby uruchomić prawdziwe wyszukiwanie:\n"
        "1. Zarejestruj się na serper.dev (darmowy plan: 2500 req/miesiąc)\n"
        "2. Dodaj SERPER_API_KEY do pliku .env\n"
        "3. Odkomentuj implementację w agent/tools.py"
    )


def tool_read_file(filepath: str, max_chars: int = 3000) -> str:
    """
    Odczytuje plik tekstowy z dysku.
    Ogranicza długość do max_chars aby nie przepełnić kontekstu.
    """
    try:
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            return f"Plik nie istnieje: {filepath}"

        with open(abs_path, encoding="utf-8") as f:
            content = f.read(max_chars)

        file_size = os.path.getsize(abs_path)
        truncated = file_size > max_chars

        result = f"Zawartość pliku: {filepath} ({file_size} bajtów)\n"
        result += "-" * 40 + "\n"
        result += content
        if truncated:
            result += f"\n...[przycięto do {max_chars} znaków]"

        return result
    except PermissionError:
        return f"Brak uprawnień do odczytu pliku: {filepath}"
    except UnicodeDecodeError:
        return f"Nie można odczytać pliku (nie jest tekstowy UTF-8): {filepath}"
    except Exception as exc:
        return f"Błąd odczytu pliku: {exc}"


# ---------------------------------------------------------------------------
# DISPATCHER – mapuje nazwę narzędzia na funkcję
# ---------------------------------------------------------------------------

_TOOL_FUNCTIONS = {
    "calculator": tool_calculator,
    "get_weather": tool_get_weather,
    "web_search": tool_web_search,
    "read_file": tool_read_file,
}


def execute_tool(name: str, inputs: dict) -> str:
    """
    Wykonaj narzędzie po nazwie i zwróć wynik jako string.

    Args:
        name: Nazwa narzędzia (musi być w _TOOL_FUNCTIONS)
        inputs: Parametry narzędzia (ze schematu input_schema)

    Returns:
        Wynik narzędzia jako string (wysyłany do Claude jako tool_result)
    """
    fn = _TOOL_FUNCTIONS.get(name)
    if fn is None:
        return f"Nieznane narzędzie: {name}"
    return fn(**inputs)
