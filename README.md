_This project has been created as part of the 42 curriculum by matalmei._

# A-Maze-ing

## Description

A-Maze-ing is a Python project from the 42 curriculum. Its goal is to generate
mazes from a configuration file, encode their walls as hexadecimal digits,
write the result to an output file, and display a visual solution path.

This repository is currently an early Slice 0 checkpoint. The configuration
parser and the first graph helper are implemented and tested. Maze generation,
path finding, serialization, display, and packaging are still planned.

## Current Status

Implemented:

- `a_maze_ing.py` parses and validates the mandatory configuration keys.
- Coordinates are converted from the subject's `(x,y)` format to internal
  `(row,column)` tuples.
- Optional integer seeds are accepted by the configuration parser.
- `maze_graph.py` counts open passages in a hexadecimal wall grid.
- 11 pytest tests currently pass.
- `maze_analyzer.py` is included as the local validation tool for future maze
  outputs.

Not implemented yet:

- `MazeGenerator` and the iterative recursive-backtracker algorithm.
- Breadth-first search and shortest-path output.
- Hexadecimal maze serialization.
- Pac-Man mode, the `42` pattern, and ASCII interaction.
- The reusable `mazegen` package build.

## Instructions

The current checkpoint requires Python 3.10 or later. A virtual environment is
recommended.

Run the current configuration parser:

```bash
python3 a_maze_ing.py config.txt
```

At this stage, the command validates the configuration and prints a summary;
it does not generate or write a maze yet.

Run the tests:

```bash
python3 -m pytest
```

Expected result for this checkpoint: 11 tests pass.

## Configuration

The configuration file uses one `KEY=VALUE` pair per line. Empty lines and
lines beginning with `#` are ignored.

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
PERFECT=False
SEED=42
OUTPUT_FILE=maze.txt
```

Mandatory keys:

- `WIDTH`: positive maze width in cells.
- `HEIGHT`: positive maze height in cells.
- `ENTRY`: entry coordinates in `(x,y)` format.
- `EXIT`: exit coordinates in `(x,y)` format, different from `ENTRY`.
- `OUTPUT_FILE`: intended output filename.
- `PERFECT`: `True`, `False`, `1`, or `0`.

Optional keys:

- `SEED`: an integer used later for reproducible maze generation.

## Planned Algorithm

The selected generation algorithm is an iterative recursive backtracker. It
will use an explicit Python list as a stack instead of Python recursion. This
keeps the traversal logic equivalent to depth-first search without depending
on the interpreter's recursion limit.

The algorithm is planned for the perfect-maze mode because it builds a
spanning tree: every cell is reachable and no cycle is introduced. Prim's and
Kruskal's algorithms may be considered later as optional extensions, but they
are not needed for the first working slice.

## Planned Output Format

Each cell will be written as one hexadecimal digit. The wall bits will be:

| Bit | Direction |
| --- | --- |
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

A set bit means that the wall is closed. Rows will be followed by an empty
line, the entry coordinates, the exit coordinates, and the shortest path using
`N`, `E`, `S`, and `W`.

## Reusable Module

The final reusable component will be a single root-level `mazegen.py` module
containing the `MazeGenerator` class. It will expose the generated structure
and a solution, accept custom dimensions and seeds, and be buildable as a
`mazegen-*` wheel or source distribution.

This module does not exist in the current checkpoint yet. The current parser
and graph helper are application groundwork, not the final reusable package.

## Roadmap

1. Complete Slice 0 with perfect-maze generation, BFS, serialization, and
   analyzer validation.
2. Add Pac-Man mode with loops, reachable corners and centre, and few dead
   ends.
3. Add the visible `42` pattern.
4. Add ASCII rendering and interactions for regeneration, path visibility, and
   wall colours.
5. Build and document the reusable package, Makefile, strict linting, and final
   delivery files.

## Project Management

The project is currently developed by `matalmei` alone, covering algorithm
design, implementation, testing, and documentation. A future collaboration
is planned, but no additional team member is listed yet.

The implementation started with a tracer-bullet approach: validate the input
boundary first, then validate the graph representation before connecting the
generator, solver, serializer, and display. This keeps each step testable and
makes the analyzer a later acceptance check instead of a last-minute debug
tool.

The incremental TDD approach has worked well for the parser and passage-count
helper. The main improvement still needed is completing the generator pipeline
so the current configuration becomes an end-to-end executable maze program.

Tools used so far include Python, `venv`, pytest, Git, the supplied
`maze_analyzer.py`, and AI assistance for subject analysis, planning, review,
and learning support. Generated suggestions are reviewed and tested before
being accepted.

## Resources

- [Mazes for Programmers](https://mazesforprogrammers.com/) by Jamis Buck.
- [Spanning tree](https://en.wikipedia.org/wiki/Spanning_tree).
- [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm).
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search).
- [Python `random` documentation](https://docs.python.org/3/library/random.html).
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
- [pytest documentation](https://docs.pytest.org/en/stable/).
- [flake8 documentation](https://flake8.pycqa.org/en/latest/).
- [mypy documentation](https://mypy.readthedocs.io/en/stable/).
- `maze_analyzer.py`, the supplied local oracle for validating generated maze
  files.

## License

The project is available under the [MIT License](LICENSE.md). The license
allows the future `mazegen` module to be reused and distributed by later
projects.
