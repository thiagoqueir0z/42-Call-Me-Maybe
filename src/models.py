"""Pydantic data models for schemas, configuration, and outputs."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

SupportedType = Literal[
    "number",
    "interger",
    "string",
    "boolean",
    "object",
    "array",
]


class TypeSchema(BaseModel):
    """Recursive JSON schema definition for parameters and return values."""

    type: SupportedType
    description: str | None = None
    properties: dict[str, "TypeSchema"] | None = None
    items: "TypeSchema | None" = None


class FunctionDefinition(BaseModel):
    """Definition of an available function from JSON input."""

    name: str
    description: str
    parameters: dict[str, TypeSchema]
    returns: TypeSchema | None = None


class PromptItem(BaseModel):
    """Single natural language prompt item from the input file."""

    prompt: str


class FunctionCallResult(BaseModel):
    """Structured function call output generated for a prompt."""

    prompt: str
    name: str
    parameters: dict[str, Any]


class AppConfig(BaseModel):
    """Validated CLI file paths for running the application."""

    functions_definition: Path
    input: Path
    output: Path


TypeSchema.model_rebuild()
