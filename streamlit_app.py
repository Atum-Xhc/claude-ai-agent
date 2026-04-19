"""
streamlit_app.py – Webowy interfejs czatu dla Claude AI Agent.

Uruchomienie:
    streamlit run streamlit_app.py
"""

import streamlit as st

from agent import ClaudeAgent, AgentConfig

# ---------------------------------------------------------------------------
# Konfiguracja strony
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Claude AI Agent",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar – ustawienia
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Ustawienia")

    model = st.selectbox(
        "Model",
        options=[
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        index=0,
    )

    max_tokens = st.slider("Max tokenów", min_value=256, max_value=8192, value=4096, step=256)
    memory_size = st.slider("Pamięć (wiad.)", min_value=4, max_value=40, value=20, step=2)

    st.divider()

    if st.button("🗑️ Wyczyść historię", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            st.session_state.agent.reset()
        st.rerun()

    st.divider()
    st.markdown("**Dostępne narzędzia:**")
    st.markdown("🔢 Kalkulator")
    st.markdown("🌤️ Pogoda (Open-Meteo)")
    st.markdown("🔍 Wyszukiwarka (mock)")
    st.markdown("📄 Czytnik plików")

    st.divider()
    st.caption("Portfolio project · Claude API")

# ---------------------------------------------------------------------------
# Inicjalizacja session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state or st.session_state.get("agent_model") != model:
    config = AgentConfig(model=model, max_tokens=max_tokens, memory_size=memory_size)
    st.session_state.agent = ClaudeAgent(config)
    st.session_state.agent_model = model

# ---------------------------------------------------------------------------
# Nagłówek
# ---------------------------------------------------------------------------
st.title("🤖 Claude AI Agent")
st.caption(f"Model: `{model}` · Max tokenów: `{max_tokens}`")

# ---------------------------------------------------------------------------
# Historia czatu
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Pokaż wywołania narzędzi jeśli są
        if msg.get("tool_calls"):
            with st.expander(f"🔧 Użyte narzędzia ({len(msg['tool_calls'])})", expanded=False):
                for tc in msg["tool_calls"]:
                    st.markdown(f"**`{tc['name']}`**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Wejście:**")
                        st.json(tc["inputs"])
                    with col2:
                        st.markdown("**Wynik:**")
                        st.code(tc["result"], language="text")

        # Metadane
        if msg.get("meta"):
            meta = msg["meta"]
            st.caption(
                f"Tokeny: {meta['input_tokens']} in / {meta['output_tokens']} out | "
                f"Iteracje: {meta['iterations']}"
            )

# ---------------------------------------------------------------------------
# Pole wprowadzania wiadomości
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Napisz wiadomość... (np. 'Ile to 15% z 240?' lub 'Jaka pogoda w Warszawie?')"):

    # Wyświetl wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Wywołaj agenta i wyświetl odpowiedź
    with st.chat_message("assistant"):
        with st.spinner("Agent myśli..."):
            response = st.session_state.agent.chat(prompt)

        st.markdown(response.text)

        # Pokaż wywołania narzędzi
        if response.tool_calls:
            tool_calls_data = [
                {
                    "name": tc.tool_name,
                    "inputs": tc.inputs,
                    "result": tc.result,
                }
                for tc in response.tool_calls
            ]
            with st.expander(f"🔧 Użyte narzędzia ({len(response.tool_calls)})", expanded=True):
                for tc in response.tool_calls:
                    st.markdown(f"**`{tc.tool_name}`**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Wejście:**")
                        st.json(tc.inputs)
                    with col2:
                        st.markdown("**Wynik:**")
                        st.code(tc.result, language="text")
        else:
            tool_calls_data = []

        # Metadane
        st.caption(
            f"Tokeny: {response.input_tokens} in / {response.output_tokens} out | "
            f"Iteracje: {response.iterations} | "
            f"Historia: {st.session_state.agent.message_count} wiad."
        )

    # Zapisz do session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.text,
        "tool_calls": tool_calls_data,
        "meta": {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "iterations": response.iterations,
        },
    })
