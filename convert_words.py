from gtts import gTTS, gTTSError
from pathlib import Path
from tqdm import tqdm


def convert_word(word: str) -> bool:
    """Converts and exports the given word to an mp3 file, accounting
    for bad internet connection, as I wrote this on the train."""
    try:
        gTTS(text=word, lang="hu", slow=False).save(f"recordings/for_typing/{word}.mp3")
        return True
    except gTTSError:
        return False


def is_to_convert(word: str, max_len: int = 10) -> bool:
    """Only convert words below the given length that haven't been converted yet."""
    return (not Path(f"recordings/for_typing/{word}.mp3").exists()) & (
        0 < len(word) <= max_len
    )


def convert_all(source_fp: str = "words.txt") -> None:
    """Converts and exports all the words listed in the given file."""
    words = Path(source_fp).read_text().split()
    for word in tqdm(words, desc="converting text to audio"):
        if is_to_convert(word):
            result = False
            while not result:
                result = convert_word(word)


if __name__ == "__main__":
    convert_all()
