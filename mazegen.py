"""Perfect maze generation, solving and hexadecimal output."""

import random
import sys
from collections import deque
from dataclasses import dataclass

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

MASK_42: tuple[tuple[int, ...], ...] = (
    (1, 0, 1, 0, 1, 1, 1),
    (1, 0, 1, 0, 0, 0, 1),
    (1, 1, 1, 0, 1, 1, 1),
    (0, 0, 1, 0, 1, 0, 0),
    (0, 0, 1, 0, 1, 1, 1),
)


@dataclass
class MazeGenerator:
    """Generate a perfect maze as a grid of wall bitmasks."""

    width: int
    height: int
    seed: int | None = None
    draw_42: bool = False

    def __post_init__(self) -> None:
        self._rng: random.Random = random.Random(self.seed)
        self.grid: list[list[int]] = [[NORTH | EAST | SOUTH | WEST
                                       for _ in range(self.width)]
                                       for _ in range(self.height)]
        self.blocked: set[tuple[int, int]] = set()

    def generate(self) -> list[list[int]]:
        """Carve a perfect maze (spanning tree) and return the grid."""
        self.blocked = self._mask_42() if self.draw_42 else set()
        self._generate_perfect()
        return self.grid

    def _mask_42(self) -> set[tuple[int, int]]:
        """Cells of the "42" pattern, or none (with a console error) if small."""
        mask_h, mask_w = len(MASK_42), len(MASK_42[0])
        if self.height < mask_h + 2 or self.width < mask_w + 2:
            print("Error: the maze is too small for the '42' pattern; "
                  "the pattern is omitted.", file=sys.stderr)
            return set()
        start_r = (self.height - mask_h) // 2
        start_c = (self.width - mask_w) // 2
        return {(start_r + r, start_c + c)
                for r, row in enumerate(MASK_42)
                for c, value in enumerate(row) if value}

    def _unvisited_neighbours(self, r: int, c: int,
                              visited: list[list[bool]]) -> list[tuple[int, int, int]]:
        """Return in-grid neighbours not yet visited, with the wall bit between."""
        out = []
        for nr, nc, side in ((r - 1, c, NORTH), (r, c + 1, EAST),
                             (r + 1, c, SOUTH), (r, c - 1, WEST)):
            if 0 <= nr < self.height and 0 <= nc < self.width \
               and not visited[nr][nc]:
                out.append((nr, nc, side))
        return out

    def _carve(self, r: int, c: int, side: int) -> None:
        """Open the wall on our side and the mirror side of the neighbour."""
        self.grid[r][c] &= ~side
        if side == NORTH:
            self.grid[r - 1][c] &= ~SOUTH
        elif side == SOUTH:
            self.grid[r + 1][c] &= ~NORTH
        elif side == EAST:
            self.grid[r][c + 1] &= ~WEST
        else:
            self.grid[r][c - 1] &= ~EAST

    def _generate_perfect(self) -> None:
        """Iterative backtracker, skipping the cells blocked by the "42"."""
        visited = [[False] * self.width for _ in range(self.height)]
        for r, c in self.blocked:
            visited[r][c] = True
        start = next(((r, c) for r in range(self.height)
                      for c in range(self.width) if not visited[r][c]), None)
        if start is None:
            return
        stack = [start]
        visited[start[0]][start[1]] = True
        while stack:
            r, c = stack[-1]
            choices = self._unvisited_neighbours(r, c, visited)
            if not choices:
                stack.pop()  # backtrack
                continue
            nr, nc, side = self._rng.choice(choices)
            self._carve(r, c, side)
            visited[nr][nc] = True
            stack.append((nr, nc))

    def solve(self, entry: tuple[int, int], exit: tuple[int, int]) -> str:
        """Return the shortest entry-to-exit path as N, E, S, W letters."""
        moves = ((NORTH, -1, 0, "N"), (EAST, 0, 1, "E"),
                 (SOUTH, 1, 0, "S"), (WEST, 0, -1, "W"))
        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        seen = {entry}
        queue: deque[tuple[int, int]] = deque([entry])
        while queue:
            cell = queue.popleft()
            if cell == exit:
                letters: list[str] = []
                while cell != entry:
                    cell, letter = parent[cell]
                    letters.append(letter)
                return "".join(reversed(letters))
            for bit, dr, dc, letter in moves:
                nxt = (cell[0] + dr, cell[1] + dc)
                if not (0 <= nxt[0] < self.height
                        and 0 <= nxt[1] < self.width):
                    continue
                if self.grid[cell[0]][cell[1]] & bit or nxt in seen:
                    continue
                seen.add(nxt)
                parent[nxt] = (cell, letter)
                queue.append(nxt)
        raise ValueError(f"no path from {entry} to {exit}")

    def write_output(self, path: str, entry: tuple[int, int],
                     exit: tuple[int, int]) -> None:
        """Write the hex grid and the entry/exit/path footer to path."""
        rows = ["".join(f"{cell:X}" for cell in row) for row in self.grid]
        path_text = self.solve(entry, exit)
        footer = f"{entry[1]},{entry[0]}\n{exit[1]},{exit[0]}\n{path_text}\n"
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(rows) + "\n\n" + footer)
