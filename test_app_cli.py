"""Application-level tests: config → CLI → output file → analyzer."""

import subprocess
import sys
from pathlib import Path

import pytest

from config import Config
from menu import _new_maze

ROOT = Path(__file__).resolve().parent


def test_new_maze_rejects_entry_inside_42(tmp_path: Path) -> None:
    config = Config(width=10, height=10, entry=(2, 1), exit=(0, 0),
                    output_file=str(tmp_path / "maze.txt"),
                    perfect=True, seed=1)
    with pytest.raises(ValueError):
        _new_maze(config)


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
