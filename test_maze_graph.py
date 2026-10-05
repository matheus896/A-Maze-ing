from maze_graph import count_open_passages


def test_fully_open_3x3_has_12_passages() -> None:
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # 0 = no wall at all
    assert count_open_passages(grid) == 12


def test_fully_closed_3x3_has_zero_passages() -> None:
    # 15 = 0b1111, all walls closed
    grid = [[15, 15, 15], [15, 15, 15], [15, 15, 15]]
    assert count_open_passages(grid) == 0


def test_coherent_single_passage() -> None:
    # two cells sharing one open wall: (0,0) East open, (0,1) West open
    grid = [[0, 2]]
    assert count_open_passages(grid) == 1
