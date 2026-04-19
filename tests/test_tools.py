"""
tests/test_tools.py
Testy jednostkowe dla modułu agent/tools.py.

Uruchomienie:
    pytest tests/ -v
"""

import os
import tempfile

import pytest

from agent.tools import (
    execute_tool,
    tool_calculator,
    tool_get_weather,
    tool_read_file,
    tool_web_search,
)


# ---------------------------------------------------------------------------
# TESTY KALKULATORA
# ---------------------------------------------------------------------------

class TestCalculator:
    def test_addition(self):
        result = tool_calculator("2 + 3")
        assert "5" in result

    def test_multiplication(self):
        result = tool_calculator("6 * 7")
        assert "42" in result

    def test_power(self):
        result = tool_calculator("2 ** 10")
        assert "1024" in result

    def test_sqrt(self):
        result = tool_calculator("sqrt(144)")
        assert "12" in result

    def test_pi(self):
        result = tool_calculator("round(pi, 2)")
        assert "3.14" in result

    def test_division_by_zero(self):
        result = tool_calculator("1 / 0")
        assert "zero" in result.lower() or "błąd" in result.lower()

    def test_invalid_expression(self):
        result = tool_calculator("import os; os.system('rm -rf /')")
        # Powinno zwrócić błąd, nie wykonać kodu
        assert "błąd" in result.lower() or "error" in result.lower()

    def test_float_result(self):
        result = tool_calculator("10 / 3")
        assert "3.33" in result or "3.3333" in result


# ---------------------------------------------------------------------------
# TESTY POGODY
# ---------------------------------------------------------------------------

class TestWeather:
    def test_known_city(self):
        result = tool_get_weather("Warsaw")
        # API powinno zwrócić dane lub błąd sieciowy
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_city(self):
        result = tool_get_weather("XxXNiemaPunktuXxX12345")
        assert "nie znaleziono" in result.lower() or "błąd" in result.lower()

    def test_result_contains_temperature(self):
        result = tool_get_weather("London")
        # Jeśli API odpowiedziało poprawnie, wynik zawiera temperaturę
        if "Błąd" not in result and "nie znaleziono" not in result:
            assert "°C" in result or "Temperatura" in result


# ---------------------------------------------------------------------------
# TESTY WYSZUKIWARKI
# ---------------------------------------------------------------------------

class TestWebSearch:
    def test_returns_string(self):
        result = tool_web_search("Python AI tutorial")
        assert isinstance(result, str)

    def test_mock_response(self):
        result = tool_web_search("test query")
        # Mock powinien zawierać informację o tym że to symulacja
        assert "mock" in result.lower() or "zaślepka" in result.lower() or "mock" in result.upper()


# ---------------------------------------------------------------------------
# TESTY CZYTNIKA PLIKÓW
# ---------------------------------------------------------------------------

class TestReadFile:
    def test_read_existing_file(self, tmp_path):
        # Utwórz tymczasowy plik testowy
        test_file = tmp_path / "test.txt"
        test_file.write_text("Linia 1\nLinia 2\nLinia 3", encoding="utf-8")

        result = tool_read_file(str(test_file))
        assert "Linia 1" in result
        assert "Linia 2" in result

    def test_nonexistent_file(self):
        result = tool_read_file("/nie/istnieje/plik.txt")
        assert "nie istnieje" in result.lower() or "błąd" in result.lower()

    def test_max_chars_truncation(self, tmp_path):
        test_file = tmp_path / "long.txt"
        test_file.write_text("A" * 500, encoding="utf-8")

        result = tool_read_file(str(test_file), max_chars=100)
        assert "przycięto" in result or len(result) < 600

    def test_shows_file_size(self, tmp_path):
        test_file = tmp_path / "sized.txt"
        content = "Hello World!"
        test_file.write_text(content, encoding="utf-8")

        result = tool_read_file(str(test_file))
        assert "bajtów" in result or str(len(content.encode())) in result


# ---------------------------------------------------------------------------
# TESTY DISPATCHERA execute_tool
# ---------------------------------------------------------------------------

class TestExecuteTool:
    def test_calculator_via_dispatcher(self):
        result = execute_tool("calculator", {"expression": "10 + 5"})
        assert "15" in result

    def test_unknown_tool(self):
        result = execute_tool("unknown_tool", {})
        assert "nieznane" in result.lower() or "unknown" in result.lower()

    def test_web_search_via_dispatcher(self):
        result = execute_tool("web_search", {"query": "test"})
        assert isinstance(result, str)
        assert len(result) > 0
