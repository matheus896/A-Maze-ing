"""Interactive terminal menu: render the maze and handle user choices."""

import os

from color import Color
from config import Config
from mazegen import EAST, SOUTH, MazeGenerator

_STEPS = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}


def clear_terminal() -> None:
    """Clear the terminal screen on Windows or Unix-like systems."""
    os.system("cls" if os.name == "nt" else "clear")


def _new_maze(config: Config) -> MazeGenerator:
    """Generate a maze from config, validate it and save its output file."""
    maze = MazeGenerator(config.width, config.height, config.seed,
                         draw_42=True)
    maze.generate()
    if config.entry in maze.blocked or config.exit in maze.blocked:
        raise ValueError("ENTRY/EXIT cannot lie inside the '42' pattern")
    maze.write_output(config.output_file, config.entry, config.exit)
    return maze


def _path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    """Return the cells a path of N/E/S/W letters walks from entry."""
    row, col = entry
    cells = {(row, col)}
    for letter in path:
        dr, dc = _STEPS[letter]
        row, col = row + dr, col + dc
        cells.add((row, col))
    return cells


def render_ascii(maze: MazeGenerator, entry: tuple[int, int],
                 exit_: tuple[int, int], show_path: bool,
                 change_color: bool) -> None:
    """Print the maze, optionally highlighting the shortest path."""
    reset = Color.RESET
    theme = Color.pick_color() if change_color else reset
    path_cells: set[tuple[int, int]] = set()
    if show_path:
        path_cells = _path_cells(entry, maze.solve(entry, exit_))
    print(theme + "+" + "---+" * maze.width + reset)
    for r in range(maze.height):
        line = theme + "|" + reset
        for c in range(maze.width):
            here = (r, c)
            if here == entry:
                content = " E "
            elif here == exit_:
                content = " X "
            elif here in maze.blocked:
                content = "███"
            elif here in path_cells:
                content = " • "
            else:
                content = "   "
            if maze.grid[r][c] & EAST:
                line += content + theme + "|" + reset
            else:
                line += content + " "
        print(line)
        border = "+"
        for c in range(maze.width):
            border += "---+" if maze.grid[r][c] & SOUTH else "   +"
        print(theme + border + reset)


def menu(config: Config) -> None:
    """Run the interactive loop: regenerate, path, colours, quit."""
    show_path = False
    maze = _new_maze(config)
    clear_terminal()
    render_ascii(maze, config.entry, config.exit, show_path, False)
    while True:
        print("1 - Re-generate a new maze and display it.")
        print("2 - Show/Hide a valid shortest path from the entrance "
              "to the exit.")
        print("3 - Change maze wall colours.")
        print("4 - Quit")
        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return
        if choice == "1":
            maze = _new_maze(config)
        elif choice == "2":
            show_path = not show_path
        elif choice == "4":
            clear_terminal()
            return
        elif choice != "3":
            clear_terminal()
            print("Please enter a number between 1 and 4.")
            continue
        clear_terminal()
        render_ascii(maze, config.entry, config.exit, show_path, choice == "3")
