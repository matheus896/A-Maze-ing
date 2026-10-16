_This project has been created as part of the 42 curriculum by matalmei, vfreitas._

# A-Maze-ing

## Description

A-Maze-ing generates mazes from a configuration file, encodes the walls of
each cell as a hexadecimal digit, writes the result to an output file, and
shows the maze in the terminal with its shortest solution path.

The project has two generation modes. With `PERFECT=True` the maze is a
perfect maze: a single path connects any two traversable cells,
so there are no loops.
With `PERFECT=False` the maze is meant to be a playable Pac-Man board, with
independent routes, reachable corners and centre, and few dead-ends.

The maze generation logic lives in a standalone `mazegen.py` module so it can
be reused by a later project. The application around it (`a_maze_ing.py`,
`config.py`, `menu.py`, `color.py`) handles the config file, the output file,
and the terminal menu.

## Current status

Implemented and validated end to end for both modes:

- Config parsing and validation, including the optional `SEED`.
- `MazeGenerator`: wall bitmask grid, iterative recursive-backtracker
  generation, seed-based reproducibility, and the visible `42` pattern made of
  fully closed cells.
- `PERFECT=True`: a perfect maze, one path between any two traversable cells.
- `PERFECT=False`: a playable Pac-Man board. The tree is braided so no real
  dead-end is left, and interior walls are opened until there are at least two
  independent routes.
- The reusable `mazegen` module is packaged as both a wheel and a source
  distribution in the repository root. Both artifacts were installed in clean
  virtual environments; the source distribution can be rebuilt from the
  checked-in project sources with `make build`.
- `solve(entry, exit)`: breadth-first search returning the shortest path as
  `N`, `E`, `S`, `W`.
- Hexadecimal output file with the entry, exit, and path footer.
- Terminal ASCII rendering with the entry, exit, path, and `42` cells, plus a
  menu to regenerate, show or hide the path, change wall colours, and quit.
- `maze_analyzer.py` reports `PERFECT maze` with `PERFECT=True` and
  `Pac-Man-USABLE` (bonus grade, no real dead-end) with `PERFECT=False`.
- All 34 tests pass; `make lint` runs `flake8` and `mypy` with the flags from
  the subject, and the `Makefile` exposes the required targets.

## Instructions

Requires Python 3.10 or later. A virtual environment is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

`make install` upgrades `pip` and installs the package plus build and development
tools (`build`, `pytest`, `flake8`, `mypy`). The module itself has no
runtime dependency.

Run the program with the config file as the only argument:

```bash
make run
```

The program writes the output file named in `OUTPUT_FILE`, prints the seed it
used, and opens the terminal menu. The `Makefile` also has `debug` (runs the
program under `pdb`), `clean` (removes `__pycache__` and the tool caches),
`lint` and `lint-strict` (the `flake8` and `mypy` commands from the subject).

Check a generated file with the analyzer supplied with the subject:

```bash
python3 maze_analyzer.py maze.txt
```

Run the tests:

```bash
python3 -m pytest
```

The suite has 34 tests covering the config parser, the graph helper, the
generator in both modes, the solver, the serializer, the `42` mask, and the
CLI.

To rebuild the distributable wheel and source archive from the repository
sources, run:

```bash
make build
```

The generated files are placed in `dist/`; the submitted copies of
`mazegen-*.whl` and `mazegen-*.tar.gz` are kept at the repository root.

## Configuration file

The config file has one `KEY=VALUE` pair per line. Empty lines and lines that
start with `#` are ignored. The mandatory keys are `WIDTH`, `HEIGHT`, `ENTRY`,
`EXIT`, `OUTPUT_FILE`, and `PERFECT`. `SEED` is optional.

Default `config.txt` in this repository:

```text
# a-maze-ing default configuration
WIDTH=12
HEIGHT=15
ENTRY=4,4
EXIT=9,9
PERFECT=False
SEED=42
OUTPUT_FILE=maze.txt
```

The default `ENTRY=4,4` and `EXIT=9,9` are valid cells for the `42` mask.
The default config exercises Pac-Man mode with a fixed seed.

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

It was chosen because it builds a spanning tree over the traversable cells:
every cell outside the `42` pattern is reachable and no cycle is created.
That is exactly what `PERFECT=True` requires: a single path between any two
cells. The traversal keeps an explicit stack instead of using Python recursion,
because the default recursion limit of about 1000 frames would break on large
mazes.

The `42` pattern is applied before carving. Its cells are marked as already
visited, so the backtracker never opens a wall in them. They stay fully closed
(`0xF`), which is how the subject asks the pattern to be drawn. If the maze is
too small for the pattern, the program prints an error on the console and
omits it, as the subject allows.

With `PERFECT=False`, the same spanning tree is post-processed. The grid is
read as a graph, where opening one wall between two already-connected cells
adds exactly one independent cycle. Every real dead-end gets one extra wall
opened so it gains a second route, and random interior walls are opened until
the board has at least two independent routes. Corners and centre stay
reachable because opening walls never disconnects the graph, and no wall is
ever opened into a `42` cell.

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
`draw_42` turns the `42` pattern on, and `perfect` selects a perfect maze
(`True`, the default) or a Pac-Man board (`False`). Entry and exit passed to
`solve` and `write_output` use internal `(row, column)` order.

The class uses only the standard library, so the module has no runtime
dependencies. The package metadata is in `pyproject.toml` at the repository
root. Run `make build` to regenerate the wheel and source distribution.

The `LICENSE.md` at the repository root is MIT, so a later project can reuse
and distribute this module.

## Team and project management

The project is developed by two students.

- `matalmei` (Matheus) worked on the input boundary (config parser), the
  `MazeGenerator` with seed-based reproducibility, the Pac-Man post-processing,
  the shortest-path solver, the serializer, and the merge of the two generation
  branches into `mazegen.py`, as well as the reusable package and its release
  artifacts. Remaining work: rehearse the defense, including a brief live
  modification.
- `vfreitas` (Vitor) worked on the iterative depth-first generation, the `42`
  mask, the ASCII display, the interactive menu, and the `Makefile`.

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

The commit-by-commit development history and the reasons for the main changes
are recorded in [RELEASE.md](RELEASE.md).

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
