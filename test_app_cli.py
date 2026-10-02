"""Application-level tests: config → CLI → output file → analyzer."""

import subprocess
import sys
from pathlib import Path

import pytest

from config import Config
from menu import _new_maze, _next_seed

ROOT = Path(__file__).resolve().parent


def test_new_maze_rejects_entry_inside_42(tmp_path: Path) -> None:
    config = Config(width=10, height=10, entry=(2, 1), exit=(0, 0),
                    output_file=str(tmp_path / "maze.txt"),
                    perfect=True, seed=1)
    with pytest.raises(ValueError):
        _new_maze(config, 1)


def test_next_seed_keeps_config_seed_on_first_run() -> None:
    config = Config(width=10, height=10, entry=(0, 0), exit=(9, 8),
                    output_file="maze.txt", perfect=True, seed=42)
    assert _next_seed(config, first=True) == 42


def test_a_new_seed_regenerates_a_different_maze(tmp_path: Path) -> None:
    out = tmp_path / "maze.txt"
    config = Config(width=10, height=10, entry=(0, 0), exit=(9, 8),
                    output_file=str(out), perfect=True, seed=42)
    _new_maze(config, 42)
    first = out.read_text(encoding="utf-8")
    _new_maze(config, 43)
    assert out.read_text(encoding="utf-8") != first


def test_cli_writes_a_perfect_maze(tmp_path: Path) -> None:
    analyzer = ROOT / "maze_analyzer.py"
    if not analyzer.exists():
        pytest.skip("maze_analyzer.py not present")
    out = tmp_path / "maze.txt"
    config = tmp_path / "config.txt"
    config.write_text(
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,8\n"
        f"PERFECT=True\nSEED=42\nOUTPUT_FILE={out}\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        [sys.executable, "a_maze_ing.py", str(config)],
        cwd=ROOT, capture_output=True, text=True,
        stdin=subprocess.DEVNULL, check=False,
    )
    assert run.returncode == 0, run.stderr
    assert out.exists()
    check = subprocess.run(
        [sys.executable, str(analyzer), str(out)],
        capture_output=True, text=True, check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr
    assert "PERFECT maze" in check.stdout
