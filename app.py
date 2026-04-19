"""
app.py – CLI do uruchamiania agenta w terminalu.

Uruchomienie:
    python app.py
"""

from agent import ClaudeAgent, AgentConfig


def print_banner():
    print("\n" + "=" * 60)
    print("  🤖  Claude AI Agent – CLI")
    print("=" * 60)
    print("  Komendy: 'quit' = wyjście, 'reset' = nowa rozmowa")
    print("  Narzędzia: kalkulator, pogoda, wyszukiwarka, plik")
    print("=" * 60 + "\n")


def main():
    config = AgentConfig()
    agent = ClaudeAgent(config)

    print_banner()
    print(f"  Model: {config.model}")
    print(f"  Max tokenów: {config.max_tokens}\n")

    while True:
        try:
            user_input = input("Ty: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nDo widzenia! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Do widzenia! 👋")
            break

        if user_input.lower() == "reset":
            agent.reset()
            print("✅ Historia konwersacji wyczyszczona.\n")
            continue

        print("\n🤔 Agent myśli...")

        response = agent.chat(user_input)

        # Pokaż jakie narzędzia zostały użyte
        if response.tool_calls:
            tools_used = ", ".join(f"🔧 {tc.tool_name}" for tc in response.tool_calls)
            print(f"  Użyte narzędzia: {tools_used}")

        print(f"\nAgent: {response.text}")
        print(
            f"\n[Tokeny: {response.input_tokens} in / {response.output_tokens} out | "
            f"Iteracje: {response.iterations} | "
            f"Historia: {agent.message_count} wiad.]\n"
        )


if __name__ == "__main__":
    main()
