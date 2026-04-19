# 🤖 Claude AI Agent

> **Portfolio project** – Średnio-zaawansowany AI Agent z narzędziami, pamięcią konwersacji i webowym UI.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Claude%20API-orange.svg)](https://anthropic.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

---

## O projekcie

Agent działa w pętli **ReAct** (Reason → Act → Observe): analizuje zapytanie użytkownika, decyduje które narzędzie wywołać, interpretuje wynik i formułuje odpowiedź. Implementuje wzorzec **Tool Use** z API Anthropic.

## Funkcjonalności

- **Tool Use** – agent sam decyduje kiedy i które narzędzie wywołać
- **Pamięć konwersacji** – sliding window, konfigurowalna liczba wiadomości
- **4 wbudowane narzędzia:**
  - 🔢 Kalkulator (wyrażenia matematyczne)
  - 🌤️ Pogoda (Open-Meteo API – darmowe, bez klucza)
  - 🔍 Wyszukiwarka (mock gotowy na Serper.dev)
  - 📄 Czytnik plików (lokalne pliki tekstowe)
- **CLI** – uruchomienie w terminalu
- **Streamlit UI** – webowy interfejs czatu

## Instalacja

```bash
git clone https://github.com/YOUR_USERNAME/claude-ai-agent.git
cd claude-ai-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
# Uzupełnij ANTHROPIC_API_KEY w pliku .env
```

## Uruchomienie

**CLI:**
```bash
python app.py
```

**Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

## Testy

```bash
pytest tests/ -v
```

## Architektura

```
agent/
├── agent.py    # ClaudeAgent – pętla ReAct, wywołania API
├── tools.py    # Definicje narzędzi (Anthropic tool schema)
└── memory.py   # ConversationMemory – sliding window
```

## Wzorce projektowe

| Wzorzec | Zastosowanie |
|---------|--------------|
| ReAct Loop | Reason → Act → Observe dla agenta |
| Tool Use | Natywne function calling Claude API |
| Sliding Window | Zarządzanie kontekstem konwersacji |
| Strategy | Łatwa podmiana implementacji narzędzi |

## Co dalej?

- [ ] Integracja z ChromaDB (pamięć semantyczna / RAG)
- [ ] FastAPI REST endpoint
- [ ] Docker deployment
- [ ] Integracja z LangChain

---

*Projekt stworzony jako część portfolio Python AI/LLM/GenAI*
