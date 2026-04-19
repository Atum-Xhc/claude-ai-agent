# 🤖 Claude AI Agent – Przewodnik krok po kroku

> Projekt portfolio: **Średnio-zaawansowany AI Agent** z narzędziami, pamięcią konwersacji i UI.  
> Stack: Python · Anthropic Claude API · Tool Use · Streamlit

---

## 📐 Architektura projektu

```
claude-ai-agent/
├── agent/
│   ├── __init__.py
│   ├── agent.py          ← Główna klasa agenta (pętla ReAct)
│   ├── tools.py          ← Narzędzia: kalkulator, wyszukiwarka, pogoda, plik
│   └── memory.py         ← Pamięć konwersacji (sliding window)
├── tests/
│   ├── __init__.py
│   └── test_tools.py     ← Testy jednostkowe narzędzi
├── app.py                ← CLI – uruchomienie w terminalu
├── streamlit_app.py      ← UI webowe (Streamlit)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Strategia gałęzi (Git Flow uproszczony)

```
main ──────────────────────────────────────────────── v1.0.0 tag
  └── develop ────────────────────────────────────── merge →  main
        ├── feature/project-setup  → merge → develop
        ├── feature/agent-core     → merge → develop
        ├── feature/tools          → merge → develop
        ├── feature/streamlit-ui   → merge → develop
        └── feature/tests          → merge → develop
```

---

## 🚀 KROK 1 – Konfiguracja środowiska lokalnego

### 1.1 Sprawdź wersję Pythona i git

```bash
python --version   # wymagane: 3.10+
git --version
```

### 1.2 Utwórz folder projektu i wirtualne środowisko

```bash
mkdir claude-ai-agent
cd claude-ai-agent

python -m venv .venv

# Aktywacja (Linux/macOS):
source .venv/bin/activate

# Aktywacja (Windows PowerShell):
.venv\Scripts\Activate.ps1
```

### 1.3 Zainstaluj zależności

```bash
pip install anthropic streamlit python-dotenv pytest httpx
pip freeze > requirements.txt
```

---

## 🐙 KROK 2 – GitHub: tworzenie repozytorium

### 2.1 Utwórz repo na GitHub

1. Wejdź na [github.com/new](https://github.com/new)
2. Nazwa: `claude-ai-agent`
3. Opis: `AI Agent with tool use powered by Claude API`
4. Ustaw jako **Public** (widoczne w portfolio)
5. **NIE** dodawaj README, .gitignore ani licencji (zrobimy to lokalnie)
6. Kliknij **Create repository**

### 2.2 Zainicjuj git lokalnie i połącz z GitHub

```bash
git init
git branch -M main

# Dodaj zdalne repozytorium (zamień YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/claude-ai-agent.git

# Sprawdź połączenie
git remote -v
```

---

## 📁 KROK 3 – Feature branch: projekt setup

```bash
# Utwórz gałąź develop i od razu feature branch
git checkout -b develop
git checkout -b feature/project-setup
```

### 3.1 Utwórz pliki konfiguracyjne

Utwórz poniższe pliki (są już gotowe w tym projekcie):
- `.gitignore` – wyklucza `.venv`, `.env`, `__pycache__` itp.
- `.env.example` – szablon zmiennych środowiskowych
- `README.md` – opis projektu

### 3.2 Pierwszy commit

```bash
git add .gitignore .env.example README.md requirements.txt
git commit -m "chore: initial project setup

- Add .gitignore for Python project
- Add .env.example with API key template
- Add README with project description
- Add requirements.txt"
```

### 3.3 Push i merge do develop

```bash
git push -u origin feature/project-setup

# Wróć na develop i zrób merge
git checkout develop
git merge --no-ff feature/project-setup -m "feat: merge project setup"
git push origin develop
```

> 💡 **Tip:** Flaga `--no-ff` (no fast-forward) tworzy commit merge, który widać w historii. Dzięki temu historia projektu jest czytelna.

---

## 🧠 KROK 4 – Feature branch: agent core

```bash
git checkout develop
git checkout -b feature/agent-core
```

### 4.1 Zaimplementuj moduły agenta

Pliki do stworzenia:
- `agent/__init__.py`
- `agent/memory.py` – klasa `ConversationMemory`
- `agent/agent.py` – klasa `ClaudeAgent` z pętlą ReAct

### 4.2 Commit po każdym module (dobra praktyka!)

```bash
# Po napisaniu memory.py:
git add agent/memory.py agent/__init__.py
git commit -m "feat(agent): add ConversationMemory with sliding window

Implements sliding window memory to limit token usage.
Keeps last N messages in context."

# Po napisaniu agent.py:
git add agent/agent.py
git commit -m "feat(agent): implement ClaudeAgent with ReAct loop

Agent calls Claude API with tool_use support.
Handles tool_result responses automatically.
Configurable max_iterations to prevent infinite loops."
```

### 4.3 Merge do develop

```bash
git checkout develop
git merge --no-ff feature/agent-core -m "feat: merge agent core implementation"
git push origin develop
```

---

## 🔧 KROK 5 – Feature branch: narzędzia (tools)

```bash
git checkout develop
git checkout -b feature/tools
```

### 5.1 Zaimplementuj narzędzia

Plik `agent/tools.py` zawiera 4 narzędzia:
- `calculator` – wyrażenia matematyczne (eval z sandboxem)
- `web_search` – symulowana wyszukiwarka (lub integracja z Serper.dev)
- `get_weather` – pogoda przez open-meteo (darmowe API, bez klucza!)
- `read_file` – odczyt pliku tekstowego z dysku

### 5.2 Commituj narzędzia po kolei

```bash
git add agent/tools.py
git commit -m "feat(tools): add calculator, weather, file reader, web search

- calculator: safe eval of math expressions
- get_weather: free Open-Meteo API (no key needed)
- read_file: read local text files
- web_search: mock implementation (ready for Serper.dev)

All tools follow Anthropic tool_use schema."
```

### 5.3 Merge do develop

```bash
git checkout develop
git merge --no-ff feature/tools -m "feat: merge tools implementation"
git push origin develop
```

---

## 🎨 KROK 6 – Feature branch: Streamlit UI

```bash
git checkout develop
git checkout -b feature/streamlit-ui
```

### 6.1 Zaimplementuj UI

Plik `streamlit_app.py` zawiera:
- Chat interface z historią
- Sidebar z konfiguracją (model, max_tokens, temperatura)
- Wyświetlanie wywołań narzędzi
- Session state dla pamięci konwersacji

### 6.2 Commit

```bash
git add streamlit_app.py
git commit -m "feat(ui): add Streamlit chat interface

- Chat UI with message history
- Tool call visualization in expander
- Configurable model settings in sidebar
- Session state for conversation persistence"
```

### 6.3 Merge do develop

```bash
git checkout develop
git merge --no-ff feature/streamlit-ui -m "feat: merge Streamlit UI"
git push origin develop
```

---

## 🧪 KROK 7 – Feature branch: testy

```bash
git checkout develop
git checkout -b feature/tests
```

### 7.1 Napisz testy

Plik `tests/test_tools.py` testuje każde narzędzie.

### 7.2 Uruchom testy

```bash
pytest tests/ -v
```

### 7.3 Commit i merge

```bash
git add tests/
git commit -m "test: add unit tests for all tools

Tests cover:
- calculator: basic ops, edge cases, division by zero
- get_weather: API response structure
- read_file: existing and non-existing files"

git checkout develop
git merge --no-ff feature/tests -m "test: merge test suite"
git push origin develop
```

---

## 🏷️ KROK 8 – Release: merge develop → main i tag

```bash
git checkout main
git merge --no-ff develop -m "release: v1.0.0 - initial release

Features:
- ClaudeAgent with ReAct loop and tool use
- Tools: calculator, weather, web search, file reader
- Conversation memory with sliding window
- CLI and Streamlit UI"

git tag -a v1.0.0 -m "v1.0.0 - initial release"
git push origin main
git push origin --tags
```

---

## ▶️ KROK 9 – Uruchomienie projektu

### 9.1 Skonfiguruj zmienne środowiskowe

```bash
cp .env.example .env
# Edytuj .env i wstaw swój klucz API:
# ANTHROPIC_API_KEY=sk-ant-...
```

Klucz API pobierzesz z: [console.anthropic.com](https://console.anthropic.com)

### 9.2 Uruchom CLI

```bash
python app.py
```

### 9.3 Uruchom Streamlit UI

```bash
streamlit run streamlit_app.py
```

Aplikacja otworzy się w przeglądarce na `http://localhost:8501`

---

## 💡 Dobre praktyki Git pokazane w tym projekcie

| Praktyka | Przykład |
|---|---|
| Konwencja commitów | `feat:`, `fix:`, `test:`, `chore:`, `docs:` |
| Feature branches | Każda funkcjonalność to osobna gałąź |
| `--no-ff` merge | Zachowuje historię feature branchy |
| Tagi wersji | `v1.0.0` dla każdego release |
| `.gitignore` | Klucze API nigdy nie wchodzą do repo |
| Atomiczne commity | Jeden commit = jedna logiczna zmiana |

---

## 🔮 Możliwe rozszerzenia (kolejne PR-y)

- [ ] `feature/langchain-integration` – przepisanie z LangChain
- [ ] `feature/vector-db` – pamięć semantyczna z ChromaDB
- [ ] `feature/docker` – Dockerfile + docker-compose
- [ ] `feature/api` – FastAPI endpoint
- [ ] `fix/rate-limiting` – obsługa limitów API Anthropic
