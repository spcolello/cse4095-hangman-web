"""Load and select words for each difficulty."""

from pathlib import Path
import secrets


DIFFICULTIES = ("easy", "medium", "hard")


class WordManager:
    def __init__(self, directory: str | Path):
        directory = Path(directory)
        self.words: dict[str, tuple[str, ...]] = {}
        for difficulty in DIFFICULTIES:
            path = directory / f"{difficulty}.txt"
            unique = set()
            for raw in path.read_text(encoding="utf-8").splitlines():
                word = raw.strip().lower()
                if not word or word.startswith("#"):
                    continue
                if not word.isascii() or not word.isalpha():
                    raise ValueError(f"Invalid word in {path}: {raw!r}")
                unique.add(word)
            if not unique:
                raise ValueError(f"No words in {path}")
            self.words[difficulty] = tuple(sorted(unique))

    def choose(self, difficulty: str) -> str:
        if difficulty not in self.words:
            raise ValueError("Difficulty must be easy, medium, or hard.")
        return secrets.choice(self.words[difficulty])
