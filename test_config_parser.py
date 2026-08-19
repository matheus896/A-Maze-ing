import pytest
from a_maze_ing import ConfigError, parse_config

BASE = (
    "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
    "PERFECT=False\nOUTPUT_FILE=maze.txt\n"
)

def _write(tmp_path, text: str) -> str:
    path = tmp_path / "config.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_valid_config_parses_with_coordinate_flip(tmp_path):
    text = (
        "# comment\n\n"
        "WIDTH=20\nHEIGHT=15\nENTRY=2,3\nEXIT=19,14\n"
        "PERFECT=False\nOUTPUT_FILE=maze.txt\nSEED=42\n"
    )
    config = parse_config(_write(tmp_path, text))
    assert config.width == 20
    assert config.height == 15
    assert config.entry == (3, 2)
    assert config.exit == (14, 19)
    assert config.output_file == "maze.txt"
    assert config.perfect is False
    assert config.seed == 42


def test_bad_width_type_raises(tmp_path):
    with pytest.raises(ConfigError):
        parse_config(_write(tmp_path, BASE.replace("WIDTH=10", "WIDTH=abc")))


def test_zero_width_semantic_error(tmp_path):
    with pytest.raises(ConfigError):
        parse_config(_write(tmp_path, BASE.replace("WIDTH=10", "WIDTH=0")))


def test_entry_out_of_bounds(tmp_path):
    with pytest.raises(ConfigError):
        parse_config(_write(tmp_path, BASE.replace("ENTRY=0,0", "ENTRY=0,12")))


def test_entry_equals_exit(tmp_path):
    with pytest.raises(ConfigError):
        parse_config(_write(tmp_path, BASE.replace("ENTRY=0,0", "ENTRY=9,9")))


def test_missing_keys_reported_together(tmp_path):
    text = BASE.replace("EXIT=9,9\n", "").replace("PERFECT=False\n", "")
    with pytest.raises(ConfigError) as excinfo:
        parse_config(_write(tmp_path, text))
    message = str(excinfo.value)
    assert "EXIT" in message and "PERFECT" in message


def test_extra_seed_key_accepted(tmp_path):
    config = parse_config(_write(tmp_path, BASE + "SEED=42\n"))
    assert config.seed == 42


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_config(str(tmp_path / "nope.txt"))