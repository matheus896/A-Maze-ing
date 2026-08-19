def count_open_passages(grid: list[list[int]]) -> int:
    """Count the open passages (edges) in the maze's passage graph."""
    rows, cols = len(grid), len(grid[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                if not (grid[r][c] & 2) and not (grid[r][c + 1] & 8):
                    count += 1
            if r + 1 < rows:
                if not (grid[r][c] & 4) and not (grid[r + 1][c] & 1):
                    count += 1
    return count