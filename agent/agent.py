"""
agent/agent.py
Główna klasa agenta – implementacja pętli ReAct z Claude API.

ReAct = Reason → Act → Observe
1. Claude analizuje zapytanie (Reason)
2. Wywołuje narzędzie (Act)
3. Dostaje wynik (Observe)
4. Formuluje odpowiedź lub kontynuuje pętlę
"""

import os
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

from .memory import ConversationMemory
from .tools import TOOLS, execute_tool

load_dotenv()


@dataclass
class AgentConfig:
    """Konfiguracja agenta – można łatwo podmienić bez modyfikacji kodu agenta."""

    model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    max_iterations: int = 10  # zabezpieczenie przed nieskończoną pętlą
    memory_size: int = 20
    system_prompt: str = (
        "Jesteś pomocnym asystentem AI z dostępem do narzędzi. "
        "Używaj narzędzi gdy potrzebujesz aktualnych danych lub obliczeń. "
        "Odpowiadaj po polsku, chyba że użytkownik pisze w innym języku. "
        "Bądź zwięzły i konkretny."
    )


@dataclass
class ToolCall:
    """Reprezentacja pojedynczego wywołania narzędzia."""

    tool_id: str
    tool_name: str
    inputs: dict
    result: str = ""


@dataclass
class AgentResponse:
    """Pełna odpowiedź agenta z metadanymi."""

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    iterations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def used_tools(self) -> list[str]:
        return [tc.tool_name for tc in self.tool_calls]


class ClaudeAgent:
    """
    Agent AI oparty na Claude API z obsługą Tool Use.

    Implementuje pętlę ReAct:
    - Wysyła zapytanie do Claude z dostępnymi narzędziami
    - Jeśli Claude chce użyć narzędzia → wykonuje je i kontynuuje
    - Kończy gdy Claude zwraca odpowiedź tekstową (stop_reason == "end_turn")

    Przykład użycia:
        agent = ClaudeAgent()
        response = agent.chat("Ile to jest 2 do potęgi 10?")
        print(response.text)
    """

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig()
        self.memory = ConversationMemory(max_messages=self.config.memory_size)
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def chat(self, user_message: str) -> AgentResponse:
        """
        Główna metoda – przyjmuje wiadomość i zwraca odpowiedź agenta.

        Args:
            user_message: Zapytanie użytkownika

        Returns:
            AgentResponse z tekstem, wywołanymi narzędziami i metadanymi
        """
        self.memory.add("user", user_message)

        tool_calls: list[ToolCall] = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        # Pętla ReAct – max max_iterations iteracji dla bezpieczeństwa
        while iterations < self.config.max_iterations:
            iterations += 1

            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=self.config.system_prompt,
                tools=TOOLS,
                messages=self.memory.get_messages(),
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            # Sprawdź czy Claude chce użyć narzędzia
            if response.stop_reason == "tool_use":
                # Dodaj odpowiedź Claude (zawiera tool_use bloki) do pamięci
                self.memory.add("assistant", response.content)

                # Wykonaj wszystkie narzędzia z tej iteracji
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_call = ToolCall(
                            tool_id=block.id,
                            tool_name=block.name,
                            inputs=block.input,
                        )
                        # Wykonaj narzędzie
                        tool_call.result = execute_tool(block.name, block.input)
                        tool_calls.append(tool_call)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_call.result,
                        })

                # Wyślij wyniki narzędzi z powrotem do Claude
                self.memory.add("user", tool_results)
                continue  # Kontynuuj pętlę – Claude sformułuje odpowiedź

            # Claude zakończył (stop_reason == "end_turn") – wyodrębnij tekst
            elif response.stop_reason == "end_turn":
                text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text += block.text

                self.memory.add("assistant", text)

                return AgentResponse(
                    text=text,
                    tool_calls=tool_calls,
                    iterations=iterations,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                )

            else:
                # Nieoczekiwany stop_reason (np. max_tokens)
                break

        # Przekroczono max_iterations lub nieoczekiwany stan
        return AgentResponse(
            text="Przepraszam, nie udało mi się przetworzyć zapytania (przekroczono limit iteracji).",
            tool_calls=tool_calls,
            iterations=iterations,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
        )

    def reset(self) -> None:
        """Wyczyść historię konwersacji (zacznij nowy czat)."""
        self.memory.clear()

    @property
    def message_count(self) -> int:
        """Liczba wiadomości w bieżącej konwersacji."""
        return len(self.memory)
