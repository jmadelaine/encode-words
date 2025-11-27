from enum import Enum
import os, re


ADDON_NAME = "Encode Words"

ADDON_DIR = os.path.dirname(__file__)


class FieldKey(Enum):
    WORD = "w"
    WORD_MEANING = "wm"
    WORD_AUDIO = "wa"
    SENTENCE = "s"
    SENTENCE_TRANSLATION = "st"
    SENTENCE_AUDIO = "sa"


class CardType(Enum):
    SEMANTIC_ENCODING = 1
    ELABORATIVE_ENCODING = 2
    FORM_ENCODING = 3


def furigana_to_html(text: str) -> str:
    """
    Convert Anki-style furigana (漢字[かんじ]) to <ruby>漢字<rt>かんじ</rt></ruby>.
    Very close to old Anki behaviour.
    """

    def repl(match):
        base = match.group(1)
        reading = match.group(2).replace(" ", "")
        return f"<ruby>{base}<rt>{reading}</rt></ruby>"

    # ([^\s\[]+)   = base (cannot contain spaces or “[”)
    # \[([^\]]+)\] = reading inside brackets
    html = re.sub(r"([^\s\[]+)\[([^\]]+)\]", repl, text)
    # Remove the space that separated two furigana blocks: </ruby> <ruby> → </ruby><ruby>
    return re.sub(r" <ruby>", "<ruby>", html)
