import os
from config import Config
from generator import Generator


def clear_terminal() -> None:
    """Clear the terminal screen on Windows or Unix-like systems."""
    os.system('cls' if os.name == 'nt' else 'clear')


def menu(config: Config) -> None:
    show_path = False
    clear_terminal()
    maze = Generator(config)
    maze.generate()
    maze.display_ascii(show_path)
    while True:
        print("1 - Re-generate a new maze and display it.")
        print("2 - Show/Hide a valid shortest path from the entrance to the exit.")
        print("3 - Change maze wall colours.")
        print("4 - Quit")

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if choice == "1":
            clear_terminal()
            maze = Generator(config)
            maze.generate()
            maze.display_ascii(show_path)
            print("New maze")
        elif choice == "2":
            clear_terminal()
            show_path = not show_path
            maze.display_ascii(show_path)
            print(f"Show path: {show_path}")
        elif choice == "3":
            clear_terminal()
            maze.display_ascii(show_path)
            print("Mudar cor")
        elif choice == "4":
            clear_terminal()
            return
        else:
            print("Please enter a number between 1 and 4.")