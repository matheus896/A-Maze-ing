import sys
from generator import Generator
from config import Config
from pathlib import Path

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")

class ConfigError(Exception):
    """Raised on any invalid configuration."""


def parse_config(path: str) -> Config:
    """Parse and validate a config file, raising ConfigError on problems."""
    raw: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ConfigError(f"line {lineno}: expected KEY=VALUE")
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if not key or not value:
                raise ConfigError(f"line {lineno}: expected KEY=VALUE")
            raw[key] = value

    missing = [key for key in MANDATORY_KEYS if key not in raw]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")

    width = _positive_int("WIDTH", raw["WIDTH"])
    height = _positive_int("HEIGHT", raw["HEIGHT"])
    entry = _coord("ENTRY", raw["ENTRY"], width, height)
    exit_ = _coord("EXIT", raw["EXIT"], width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
    perfect = _bool("PERFECT", raw["PERFECT"])
    seed = _optional_int("SEED", raw)
    return Config(width, height, entry, exit_,
                  raw["OUTPUT_FILE"], perfect, seed)


def _positive_int(key: str, value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ConfigError(f"{key} must be a positive integer") from None
    if number <= 0:
        raise ConfigError(f"{key} must be a positive integer")
    return number


def _coord(key: str, value: str, width: int, height: int) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be x,y coordinates")
    try:
        x, y = int(parts[0]), int(parts[1])
    except ValueError:
        raise ConfigError(f"{key} must be x,y coordinates") from None
    if not (0 <= y < height and 0 <= x < width):
        raise ConfigError(f"{key} is outside the maze bounds")
    return (y, x)


def _bool(key: str, value: str) -> bool:
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise ConfigError(f"{key} must be True or False")


def _optional_int(key: str, raw: dict[str, str]) -> int | None:
    if key not in raw:
        return None
    try:
        return int(raw[key])
    except ValueError:
        raise ConfigError(f"{key} must be an integer") from None


def main(argv: list[str]) -> int:
    """Parse the config and print a summary (generator arrives next)."""
    if len(argv) != 2:
        print(f"usage: python3 {Path(argv[0]).name} config.txt",
              file=sys.stderr)
        return 1
    try:
        config = parse_config(argv[1])
        print(f"parsed: {config.width}x{config.height} perfect={config.perfect}")
        maze = Generator(config)
        maze.display_ascii()
        maze.generate()
        maze.display_ascii()
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: config file not found: {argv[1]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
