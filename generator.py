import random
from config import Config
from color import Color


class Generator:

    WALL_NORTH: int = 1
    WALL_EAST: int = 2
    WALL_SOUTH: int = 4
    WALL_WEST: int = 8

    _PATTERN_42: list[list[int]] = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]

    def __init__(self, config: Config) -> None:
        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit = config.exit
        self.output_file = config.output_file
        self.perfect = config.perfect
        self.seed = config.seed

        self.grid: list[list[int]] = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]

        self.visited: set[tuple[int, int]] = set()
        self.blocked_cells: set[tuple[int, int]] = set()

    def generate(self) -> None:
        self.apply_mask()
        self.run_dfs()

    def apply_mask(self) -> None:
        mask_h = len(self._PATTERN_42)
        mask_w = len(self._PATTERN_42[0])

        if self.height < mask_h + 2 or self.width < mask_w + 2:
            return

        start_y = (self.height - mask_h) // 2
        start_x = (self.width - mask_w) // 2

        for r, row in enumerate(self._PATTERN_42):
            for c, val in enumerate(row):
                if val == 1:
                    x = start_x + c
                    y = start_y + r
                    self.blocked_cells.add((x, y))
                    self.visited.add((x, y))


    def run_dfs(self) -> None:
        current = self.entry
        stack: list[tuple[int, int]] = [current]
        self.visited.add(current)

        directions = [
            (0, -1, self.WALL_NORTH, self.WALL_SOUTH),
            (1, 0, self.WALL_EAST, self.WALL_WEST),
            (0, 1, self.WALL_SOUTH, self.WALL_NORTH),
            (-1, 0, self.WALL_WEST, self.WALL_EAST),
        ]

        while stack:
            cX, cY = stack[-1]
            univisited_neighbors: list[tuple[int, int, int, int]] = []

            for dX, dY, wall_curr, wall_nei in directions:
                nX, nY = cX + dX, cY + dY

                if 0 <= nX < self.width and 0 <= nY < self.height:
                    if (nX, nY) not in self.visited:
                        univisited_neighbors.append((nX, nY, wall_curr, wall_nei))

            if univisited_neighbors:
                nX, nY, wall_curr, wall_nei = random.choice(univisited_neighbors)

                self.grid[cY][cX] &= ~wall_curr
                self.grid[nY][nX] &= ~wall_nei

                self.visited.add((nX, nY))
                stack.append((nX, nY))
            else:
                stack.pop()

    def display_ascii(self, show_path: bool, change_color: bool) -> None:
        """Render ASCII representation directly in terminal with highlighted mask."""
        if change_color:
            theme = Color.pick_color()
        else:
            theme = Color.RESET
        print(theme + "+" + "---+" * self.width + Color.RESET)
        for y in range(self.height):
            row_str = theme + "|" + Color.RESET
            for x in range(self.width):
                cell = self.grid[y][x]

                if (x, y) == self.entry:
                    content = " E "
                elif (x, y) == self.exit:
                    content = " X "
                elif (x, y) in self.blocked_cells:
                    content = "███"
                else:
                    content = "   "

                row_str += f"{content}{theme}|{Color.RESET}" if (cell & self.WALL_EAST) else f"{content} "
            print(row_str)

            bottom_str = "+"
            for x in range(self.width):
                cell = self.grid[y][x]
                bottom_str += "---+" if (cell & self.WALL_SOUTH) else "   +"
            print(theme + bottom_str + Color.RESET)