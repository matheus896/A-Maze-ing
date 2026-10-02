import subprocess
import sys
from collections import deque
from pathlib import Path

import pytest

from mazegen import MazeGenerator, NORTH, EAST, SOUTH, WEST
from maze_graph import count_open_passages

HEX_DIGITS = set("0123456789abcdefABCDEF")
MOVES = {
    "N": (-1, 0, NORTH),
    "E": (0, 1, EAST),
    "S": (1, 0, SOUTH),
    "W": (0, -1, WEST),
}


def _reachable_count(grid: list[list[int]]) -> int:
    """Flood-fill from (0,0) through open passages; return cells reached."""
    rows, cols = len(grid), len(grid[0])
    seen: set[tuple[int, int]] = {(0, 0)}
    stack: list[tuple[int, int]] = [(0, 0)]
    while stack:
        r, c = stack.pop()
        cell = grid[r][c]
        for nr, nc, bit in ((r - 1, c, NORTH), (r, c + 1, EAST),
                            (r + 1, c, SOUTH), (r, c - 1, WEST)):
            if 0 <= nr < rows and 0 <= nc < cols \
                and not (cell & bit) and (nr, nc) not in seen:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return len(seen)


def _make(grid: list[list[int]]) -> MazeGenerator:
    """Build a generator over a hand-crafted, coherent grid."""
    gen = MazeGenerator(width=len(grid[0]), height=len(grid), seed=0)
    gen.grid = [row[:] for row in grid]
    return gen


def _walk(gen: MazeGenerator, entry: tuple[int, int],
          path: str) -> tuple[int, int]:
    """Apply a path, asserting every step crosses an open wall."""
    row, col = entry
    for letter in path:
        dr, dc, bit = MOVES[letter]
        assert not gen.grid[row][col] & bit
        row, col = row + dr, col + dc
    return (row, col)


def _bfs_distance(grid: list[list[int]], start: tuple[int, int],
                  goal: tuple[int, int]) -> int:
    """Independent reference: shortest distance, or -1 when unreachable."""
    dist: dict[tuple[int, int], int] = {start: 0}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        row, col = queue.popleft()
        for dr, dc, bit, back in ((-1, 0, NORTH, SOUTH), (0, 1, EAST, WEST),
                                  (1, 0, SOUTH, NORTH), (0, -1, WEST, EAST)):
            nxt = (row + dr, col + dc)
            if not (0 <= nxt[0] < len(grid) and 0 <= nxt[1] < len(grid[0])):
                continue
            if grid[row][col] & bit or grid[nxt[0]][nxt[1]] & back:
                continue
            if nxt not in dist:
                dist[nxt] = dist[(row, col)] + 1
                queue.append(nxt)
    return dist.get(goal, -1)


def test_perfect_5x5_has_24_open_passages():
    gen = MazeGenerator(width=5, height=5, seed=7)
    gen.generate()
    assert count_open_passages(gen.grid) == 24


def test_perfect_5x5_reaches_every_cell():
    gen = MazeGenerator(width=5, height=5, seed=7)
    gen.generate()
    assert _reachable_count(gen.grid) == 25


def test_walls_are_coherent():
    gen = MazeGenerator(width=5, height=5, seed=7)
    gen.generate()
    rows, cols = len(gen.grid), len(gen.grid[0])
    for r in range(rows):
        for c in range(cols):
            cell = gen.grid[r][c]
            if c + 1 < cols:
                assert bool(cell & EAST) == bool(gen.grid[r][c + 1] & WEST)
            if r + 1 < rows:
                assert bool(cell & SOUTH) == bool(gen.grid[r + 1][c] & NORTH)


def test_same_seed_produces_same_maze():
    a = MazeGenerator(width=5, height=5, seed=7)
    b = MazeGenerator(width=5, height=5, seed=7)
    a.generate()
    b.generate()
    assert a.grid == b.grid


STRAIGHT_CORRIDOR = [[0xB], [0xA], [0xE]]
TURN_EAST_SOUTH = [[0xD, 0x3], [0xF, 0xE]]
SHORTCUT_WITH_DECOY = [[9, 5, 3], [12, 5, 6]]


def test_solve_straight_corridor_uses_north() -> None:
    assert _make(STRAIGHT_CORRIDOR).solve((2, 0), (0, 0)) == "NN"


def test_solve_turn_uses_east_and_south() -> None:
    assert _make(TURN_EAST_SOUTH).solve((0, 0), (1, 1)) == "ES"


def test_solve_prefers_the_shortcut_over_the_decoy() -> None:
    assert _make(SHORTCUT_WITH_DECOY).solve((0, 0), (0, 2)) == "EE"


def test_solve_matches_reference_distance_on_generated_maze() -> None:
    gen = MazeGenerator(width=5, height=5, seed=7)
    gen.generate()
    entry, exit_ = (0, 0), (4, 4)
    path = gen.solve(entry, exit_)
    assert _walk(gen, entry, path) == exit_
    assert len(path) == _bfs_distance(gen.grid, entry, exit_)


def test_solve_raises_when_exit_is_unreachable() -> None:
    gen = _make([[0xF, 0xF]])
    with pytest.raises(ValueError):
        gen.solve((0, 0), (0, 1))


def test_write_output_has_grid_blank_line_and_footer(tmp_path: Path) -> None:
    gen = MazeGenerator(width=3, height=2, seed=7)
    gen.generate()
    entry, exit_ = (0, 0), (1, 2)
    out = tmp_path / "maze.txt"
    gen.write_output(str(out), entry, exit_)
    lines = out.read_text(encoding="utf-8").split("\n")
    assert len(lines) == 2 + 1 + 3 + 1
    assert all(len(row) == 3 for row in lines[:2])
    assert all(char in HEX_DIGITS for row in lines[:2] for char in row)
    assert lines[2] == ""
    assert lines[3] == "0,0"
    assert lines[4] == "2,1"
    assert lines[5] == gen.solve(entry, exit_)
    assert _walk(gen, entry, lines[5]) == exit_
    assert lines[6] == ""


def test_analyzer_accepts_perfect_output(tmp_path: Path) -> None:
    analyzer = Path(__file__).resolve().parent / "maze_analyzer.py"
    if not analyzer.exists():
        pytest.skip("maze_analyzer.py not present")
    gen = MazeGenerator(width=5, height=5, seed=7)
    gen.generate()
    out = tmp_path / "maze.txt"
    gen.write_output(str(out), (0, 0), (4, 4))
    result = subprocess.run(
        [sys.executable, str(analyzer), str(out)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PERFECT maze" in result.stdout


def test_draw_42_cells_are_fully_closed() -> None:
    gen = MazeGenerator(width=10, height=10, seed=42, draw_42=True)
    gen.generate()
    assert gen.blocked
    assert all(gen.grid[r][c] == 0xF for r, c in gen.blocked)
    assert _reachable_count(gen.grid) == 100 - len(gen.blocked)
