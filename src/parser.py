"""Safe JSON file reader and writer with Pydantic schema validation."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError

from src.models import FunctionCallResult, FunctionDefinition, PromptItem


class ParserError(Exception):
    """Raised when reading, validating, or writing JSON files fails."""


class FileParser(BaseModel):
    """Reads, validates, and writes project JSON files."""

    @staticmethod
    def _read_json_list(file_path: Path) -> list[Any]:
        """Read a JSON file and ensure its root value is a list."""
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data: Any = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ParserError(
                f"Malformed JSON in '{file_path}' "
                f"(line {exc.lineno}, col {exc.colno}): {exc.msg}"
            ) from exc
        except (OSError, UnicodeDecodeError) as exc:
            raise ParserError(
                f"Cannot read file '{file_path}': {exc}"
            ) from exc

        if not isinstance(data, list):
            raise ParserError(
                f"Expected a JSON array in '{file_path}', "
                f"got {type(data).__name__}."
            )
        return data

    @staticmethod
    def load_functions(file_path: Path) -> list[FunctionDefinition]:
        """Load and validate function definitions from a JSON file."""
        raw_data = FileParser._read_json_list(file_path)
        if not raw_data:
            raise ParserError(
                f"Function definitions list in '{file_path}' is empty."
            )
        try:
            adapter = TypeAdapter(list[FunctionDefinition])
            functions = adapter.validate_python(raw_data)
        except ValidationError as exc:
            raise ParserError(
                f"Invalid function schema in '{file_path}': {exc}"
            ) from exc
        seen_names: set[str] = set()
        for func in functions:
            if func.name in seen_names:
                raise ParserError(
                    f"Duplicate function '{func.name}' in '{file_path}'."
                )
            seen_names.add(func.name)

        return functions

    @staticmethod
    def load_prompts(file_path: Path) -> list[PromptItem]:
        """Load and validate natural language prompts from a JSON file."""
        raw_data = FileParser._read_json_list(file_path)
        try:
            adapter = TypeAdapter(list[PromptItem])
            return adapter.validate_python(raw_data)
        except ValidationError as exc:
            raise ParserError(
                f"Invalid prompt schema in '{file_path}': {exc}"
            ) from exc

    @staticmethod
    def save_results(
        file_path: Path,
        results: list[FunctionCallResult]
    ) -> None:
        """Serialize and write function call results to a JSON file."""
        payload = [result.model_dump() for result in results]
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        except OSError as exc:
            raise ParserError(
                f"Failed to write output file '{file_path}': {exc}"
            ) from exc
