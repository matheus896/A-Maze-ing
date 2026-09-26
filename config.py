from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """Parsed and validated maze configuration."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None