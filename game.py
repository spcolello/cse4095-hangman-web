"""Framework-independent Hangman rules."""

from dataclasses import dataclass, field


class InvalidGuess(ValueError):
    """A letter is malformed, repeated, or submitted after the game ends."""


@dataclass
class HangmanGame:
    word: str
    difficulty: str
    max_misses: int = 6
    guessed_letters: list[str] = field(default_factory=list)
    incorrect_letters: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.word = self.word.lower()
        if not self.word.isascii() or not self.word.isalpha():
            raise ValueError("The secret word must contain only A-Z letters.")
        if self.max_misses < 1:
            raise ValueError("At least one incorrect guess must be allowed.")

    @property
    def status(self) -> str:
        if all(letter in self.guessed_letters for letter in self.word):
            return "won"
        if len(self.incorrect_letters) >= self.max_misses:
            return "lost"
        return "playing"

    @property
    def remaining_guesses(self) -> int:
        return self.max_misses - len(self.incorrect_letters)

    @property
    def pattern(self) -> str:
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.word)

    def guess(self, letter: str) -> bool:
        if self.status != "playing":
            raise InvalidGuess("This game has ended. Start a new game to keep playing.")
        if not isinstance(letter, str) or len(letter) != 1 or not letter.isascii() or not letter.isalpha():
            raise InvalidGuess("Enter one letter from A to Z.")
        letter = letter.lower()
        if letter in self.guessed_letters:
            raise InvalidGuess(f"You already guessed {letter.upper()}.")
        self.guessed_letters.append(letter)
        correct = letter in self.word
        if not correct:
            self.incorrect_letters.append(letter)
        return correct

    def public_state(self) -> dict:
        state = {
            "difficulty": self.difficulty,
            "pattern": self.pattern,
            "guessed_letters": list(self.guessed_letters),
            "incorrect_letters": list(self.incorrect_letters),
            "remaining_guesses": self.remaining_guesses,
            "max_incorrect_guesses": self.max_misses,
            "status": self.status,
        }
        if self.status != "playing":
            state["word"] = self.word
        return state
