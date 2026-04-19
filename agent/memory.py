"""
agent/memory.py
Pamięć konwersacji z algorytmem sliding window.
Ogranicza liczbę wiadomości w kontekście, aby nie przekraczać limitu tokenów.
"""

from typing import Literal


class ConversationMemory:
    """
    Przechowuje historię wiadomości w formacie oczekiwanym przez Claude API.
    Implementuje sliding window – trzyma ostatnie `max_messages` wiadomości.

    Przykład użycia:
        memory = ConversationMemory(max_messages=20)
        memory.add("user", "Cześć!")
        memory.add("assistant", "Hej! Jak mogę pomóc?")
        messages = memory.get_messages()
    """

    def __init__(self, max_messages: int = 20):
        """
        Args:
            max_messages: Maksymalna liczba wiadomości w pamięci.
                          Starsza historia jest przycinana (sliding window).
        """
        self.max_messages = max_messages
        self._messages: list[dict] = []

    def add(self, role: Literal["user", "assistant"], content: str | list) -> None:
        """
        Dodaj wiadomość do pamięci.

        Args:
            role: "user" lub "assistant"
            content: Tekst lub lista bloków (dla tool_use/tool_result)
        """
        self._messages.append({"role": role, "content": content})
        self._trim()

    def get_messages(self) -> list[dict]:
        """Zwróć listę wiadomości gotową do wysłania do Claude API."""
        return self._messages.copy()

    def clear(self) -> None:
        """Wyczyść całą historię konwersacji."""
        self._messages = []

    def _trim(self) -> None:
        """Przytnij historię do max_messages (sliding window)."""
        if len(self._messages) > self.max_messages:
            # Zawsze usuwaj pary (user + assistant) żeby nie zostawić osieroconych wiadomości
            excess = len(self._messages) - self.max_messages
            self._messages = self._messages[excess:]

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"ConversationMemory(messages={len(self)}, max={self.max_messages})"
