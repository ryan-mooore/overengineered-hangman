from __future__ import annotations

import json
import random
from os import path, system, name
from string import ascii_lowercase
from types import SimpleNamespace as Namespace
from typing import Callable, List, Optional


class HangmanWord:
    """
    Represents the word to guess in a game of Hangman.


    Attributes
    ----------
    word : List[HangmanWord.HangmanChar]
        list of HangmanChar subclass instances that forms the word
    """
    class HangmanChar:
        """
        Represents one character in the word in a game of Hangman.
        Can be guessable (alpha char) or non-guessable.


        Attributes
        ----------
        char : str
            string representation of the character
        guessed : bool
            whether the player has guessed this character correctly yet
        
        Properties
        ----------
        guessable : bool
            represents whether the char is and alpha char and thus can be guessed
        """
        def __init__(self, char: str) -> None:
            """
            Parameters
            ----------
            char : str
                actual character which will become the string representation
            """
            self.char: str = char
            self.guessed: bool = False

        @property
        def guessable(self) -> bool:
            return self.char in ascii_lowercase

        def display(self) -> str:
            if self.guessable:
                return self.char if self.guessed else '_'
            else:
                return self.char

        def __str__(self) -> str:
            return self.char

        def __repr__(self) -> str:
            return f"{self.__class__!r}: {self!s}"

    def __init__(self, word: str) -> None:
        """
        Parameters
        ----------
        word : str
            actual word which will become the string representation
        """
        self.word: List[HangmanWord.HangmanChar] = [self.HangmanChar(char) for char in word]

    @classmethod
    def from_config(cls, config: Namespace) -> HangmanWord:
        """
        Creates a HangmanWord instance randomly from the config settings

        Parameters
        ----------
        config : Namespace(
            difficulty=20000,
            selection_range=400,
            use_punctuated=False,
            lives=10,
            lose_life_on_duplicate_guess=False,
            words_json="words.json"
        )
            config namespace object containing settings for this game 
        """

        words = cls._load_words(config).words

        choices: List[Namespace] = sorted(
            words,
            key=lambda word: abs(word.frequency - config.difficulty)
        )[:config.selection_range]

        while True:
            word: HangmanWord = cls(random.choice(choices).word)
            if not config.use_punctuated and not str(word).isalpha():
                continue
            break
        return word

    @staticmethod
    def _load_words(config) -> Namespace:
        with open(path.join(path.dirname(__file__), config.words_json)) as words_json:
            return json.loads(
                words_json.read(),
                object_hook=lambda d: Namespace(**d)
            )

    def get_chars(self) -> list[str]:
        return [char.char for char in self.word]

    def __str__(self) -> str:
        return ''.join(self.get_chars())

    def __repr__(self) -> str:
        return f"{self.__class__!r}: {self!s}"

    def display(self) -> str:
        return ' '.join([char.display() for char in self.word])

    def has_won(self) -> bool:
        for char in self.word:
            if char.guessable:
                if not char.guessed:
                    return False
        return True


class Guess:
    """
    Represents a guessed character in the game.


    Attributes
    ----------
    char : str
        string representation of the character
    correct : bool
        whether the character is in the word or not
    """
    def __init__(self, char: str) -> None:
        """
        Parameters
        char : str
            actual character which will become the string representation
        """
        self.char: str = char
        self.correct: Optional[bool] = None

    def guess(self, game: Game) -> Optional[bool]:
        if self.char in [guess.char for guess in game.guesses]:
            self.correct = False if game.config.lose_life_on_duplicate_guess else None
        else:
            if self.char in game.word.get_chars():
                self.correct = True
                for correct_char in game.word.word:
                    if correct_char.char == self.char:
                        correct_char.guessed = True
            else:
                self.correct = False
        return self.correct

    def __str__(self) -> str:
        return self.char

    def __repr__(self) -> str:
        return f"{'correct' if self.correct else 'incorrect'} {self.__class__!r} of {self!s}"


class Game:
    """
    Represents a game of hangman.


    Attributes
    ----------
    config : SimpleNamespace
        contains settings related to the game in SimpleNamespace format
    word : HangmanWord
        the HangmanWord class instance being guessed in this game
    guesses : List[Guess]
        contains all guess history in list format
    lives : int
        how many lives the player has left in the current game
    """
    clear: Callable[[], int] = lambda: system('cls' if name == 'nt' else 'clear')

    def __init__(self, config: Namespace) -> None:
        """
        Parameters
        ----------
        config : Namespace(
            difficulty=20000,
            selection_range=400,
            use_punctuated=False,
            lives=10,
            lose_life_on_duplicate_guess=False,
            words_json="words.json"
        )
            config namespace object containing settings for this game
        """
        self.config = config

        self.word = HangmanWord.from_config(self.config)
        self.guesses: List[Guess] = []
        self.lives = self.config.lives

    def turn(self) -> Optional[bool]:
        self.paint_UI()

        if self.word.has_won():
            self.paint_endgame_UI(won=True)
            return True
        if self.lives == 0:
            self.paint_endgame_UI(won=False)
            return False

        guess = self.get_guess()
        if guess.guess(self) is False:
            self.lives -= 1
        self.guesses.append(guess)
        return None

    @staticmethod
    def get_guess() -> Guess:
        while True:
            char: str = input("guess char: ")
            if char in ascii_lowercase and char:
                return Guess(char)

    def start(self) -> None:
        while True:
            if self.turn() is not None:
                break

    def paint_UI(self) -> None:
        self.__class__.clear()
        print(f"{self.lives} / {self.config.lives}")
        print(self.word.display())
        print(', '.join([str(guess) for guess in self.guesses]))

    def paint_endgame_UI(self, won: bool = False) -> None:
        self.__class__.clear()
        print("the word was:")
        print(' '.join(str(self.word)))
        print(f"you {'won' if won else 'lost'}")


if __name__ == "__main__":
    game = Game(Namespace(**{
        "difficulty": 20000,
        "selection_range": 400,
        "use_punctuated": False,
        "lives": 10,
        "lose_life_on_duplicate_guess": False,
        "words_json": "words.json"
    }))
    game.start()