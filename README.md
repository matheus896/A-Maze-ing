_This project has been created as part of the 42 curriculum by matalmei, vfreitas._

# A-Maze-ing

## Description

A-Maze-ing generates mazes from a configuration file, encodes the walls of
each cell as a hexadecimal digit, writes the result to an output file, and
shows the maze in the terminal with its shortest solution path.

The project has two generation modes. With `PERFECT=True` the maze is a
perfect maze: a single path connects any two cells, so there are no loops.
With `PERFECT=False` the maze is meant to be a playable Pac-Man board, with
independent routes, reachable corners and centre, and few dead-ends.

The maze generation logic lives in a standalone `mazegen.py` module so it can
be reused by a later project. The application around it (`a_maze_ing.py`,
`config.py`, `menu.py`, `color.py`) handles the config file, the output file,
and the terminal menu.

## Current status

Implemented and passing the `PERFECT=True` contract end to end:

- Config parsing and validation, including the optional `SEED`.
- `MazeGenerator`: wall bitmask grid, iterative recursive-backtracker
  generation, seed-based reproducibility, and the visible `42` pattern made of
  fully closed cells.
- `solve(entry, exit)`: breadth-first search returning the shortest path as
  `N`, `E`, `S`, `W`.
- Hexadecimal output file with the entry, exit, and path footer.
- Terminal ASCII rendering with the entry, exit, path, and `42` cells, plus a
  menu to regenerate, show or hide the path, change wall colours, and quit.
- `maze_analyzer.py` reports `PERFECT maze` for the current default output.

Still to do:

- `PERFECT=False` (Pac-Man mode) is read from the config but not yet applied:
  the generator always builds a perfect maze. This is the next slice.
- Makefile, `pyproject.toml`, wheel and source build, and the `flake8` and
  `mypy` lint pass.

## Instructions

Requires Python 3.10 or later. A virtual environment is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pytest
```

Run the program with the config file as the only argument:

```bash
python3 a_maze_ing.py config.txt
```

The program writes the output file named in `OUTPUT_FILE`, prints the seed it
used, and opens the terminal menu.

Check a generated file with the analyzer supplied with the subject:

```bash
python3 maze_analyzer.py maze.txt
```

Run the tests:

```bash
python3 -m pytest
```

The current suite has 27 tests covering the config parser, the graph helper,
the generator, the solver, the serializer, the `42` mask, and the CLI.

## Configuration file

The config file has one `KEY=VALUE` pair per line. Empty lines and lines that
start with `#` are ignored. The mandatory keys are `WIDTH`, `HEIGHT`, `ENTRY`,
`EXIT`, `OUTPUT_FILE`, and `PERFECT`. `SEED` is optional.

Default `config.txt` in this repository:

```text
# a-maze-ing default configuration
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=9,8
PERFECT=True
SEED=42
OUTPUT_FILE=maze.txt
```

| Key | Mandatory | Meaning |
| --- | --- | --- |
| `WIDTH` | yes | Maze width in cells. |
| `HEIGHT` | yes | Maze height in cells. |
| `ENTRY` | yes | Entry cell as `x,y`, inside the bounds. |
| `EXIT` | yes | Exit cell as `x,y`, inside the bounds and different from `ENTRY`. |
| `PERFECT` | yes | `True` or `False` (`1` and `0` also accepted). |
| `SEED` | no | Integer seed for reproducible generation. If absent, a seed is drawn and printed. |
| `OUTPUT_FILE` | yes | Path of the file the maze is written to. |

Coordinates in the config use the subject `x,y` order. Inside the code the
coordinates are stored as `(row, column)`; `write_output` converts back to
`x,y` for the footer.

## Output file format

Every cell is one hexadecimal digit. A set bit means the wall is closed:

| Bit | Direction |
| --- | --- |
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

Rows are written one per line. After an empty line come three footer lines:
the entry coordinates, the exit coordinates, and the shortest path from entry
to exit using the letters `N`, `E`, `S`, `W`. Every line ends with `\n`.

## Generation algorithm

The generator uses an iterative recursive backtracker, which is a
depth-first search that carves passages as it visits cells.

It was chosen because it builds a spanning tree over the cells: every cell is
reachable and no cycle is created. That is exactly what `PERFECT=True`
requires, a single path between any two cells. The traversal keeps an explicit
list as a stack instead of using Python recursion, because the default
recursion limit of about 1000 frames would break on large mazes.

The `42` pattern is applied before carving. Its cells are marked as already
visited, so the backtracker never opens a wall in them. They stay fully closed
(`0xF`), which is how the subject asks the pattern to be drawn. If the maze is
too small for the pattern, the program prints an error on the console and
omits it, as the subject allows.

`PERFECT=False` will reuse the same spanning tree and then open extra walls to
create loops, and braid the dead-ends. That work is not finished yet.

## Reusable module

The reusable part is `mazegen.py`, which contains the `MazeGenerator` class
and nothing tied to the terminal or the config file. It exposes the generated
structure through `grid` and the blocked `42` cells through `blocked`, and it
computes a solution with `solve`.

```python
from mazegen import MazeGenerator

maze = MazeGenerator(width=20, height=15, seed=42, draw_42=True)
maze.generate()

maze.solve((0, 0), (14, 19))              # "(row, col)" -> "EESS..."
maze.write_output("maze.txt", (0, 0), (14, 19))
```

`width` and `height` are required. `seed` makes the output reproducible.
`draw_42` turns the `42` pattern on. Entry and exit passed to `solve` and
`write_output` use internal `(row, column)` order.

The class uses only the standard library, so the module has no runtime
dependencies. It will be packaged as `mazegen-*` (wheel and source
distribution) from a `pyproject.toml` at the repository root. The packaging
files are not in place yet.

The `LICENSE.md` at the repository root is MIT, so a later project can reuse
and distribute this module.

## Team and project management

The project is developed by two students.

- `matalmei` (Matheus) worked on the input boundary (config parser), the
  `MazeGenerator` with seed-based reproducibility, the shortest-path solver,
  the serializer, and the merge of the two generation branches into
  `mazegen.py`. The remaining planned work on this side is the Makefile, the
  package build, the lint pass, and this README.
- `vfreitas` (Vitor) worked on the iterative depth-first generation, the `42`
  mask, the ASCII display, and the interactive menu.

Planning started with a tracer bullet: get the thinnest path that crosses the
whole system from the config file to an analyzer-approved output, then grow it
slice by slice. The input boundary came first, then the graph helpers, then
generation, solving, serialization, display, and interactions. Each slice was
checked against `maze_analyzer.py` before moving on.

What worked well: the analyzer as an oracle after every change, seed-based
reproducibility for debugging, and tests written before the implementation.
What could improve: the README fell behind the code during the work, the two
students built two separate generators at the start and paid for it in a merge,
and a coordinate swap between the internal `(row, column)` order and the `x,y`
footer cost debugging time because it failed silently.

Tools used: Python 3.10+, `venv`, pytest, Git and GitHub, the supplied
`maze_analyzer.py`, and AI assistance described below.

## Resources

Classic references:

- [Mazes for Programmers](https://mazesforprogrammers.com/) by Jamis Buck.
- [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm).
- [Spanning tree](https://en.wikipedia.org/wiki/Spanning_tree).
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search).
- [Python `random` documentation](https://docs.python.org/3/library/random.html).
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
- [pytest documentation](https://docs.pytest.org/en/stable/).
- [flake8 documentation](https://flake8.pycqa.org/en/latest/).
- [mypy documentation](https://mypy.readthedocs.io/en/stable/).
- `maze_analyzer.py`, the local oracle supplied with the subject.

How AI was used: AI supported subject analysis and slice planning, explanations
of the algorithms from first principles, validation of algorithm approaches
against a reference outside the repository, the writing of the test suite, and
the preparation of mechanical files such as the Makefile and packaging
metadata. The team reviewed and tested every suggestion before accepting it,
and wrote the core implementation so it can be explained during the defense.
No generated content was accepted without understanding it.

## License

The project is available under the [MIT License](LICENSE.md), which allows the
`mazegen` module to be reused and distributed by later projects.
