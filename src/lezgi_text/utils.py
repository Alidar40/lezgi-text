import re
import string

import numpy as np
import fasttext
from nltk.tokenize import word_tokenize
from huggingface_hub import hf_hub_download


PALOCHKA = 'Ӏ'


def canonize_lez(text: str) -> str:
    global PALOCHKA

    for abruptive_letter in ['к', 'К', 'п', 'П', 'т', 'Т', 'ц', 'Ц', 'ч', 'Ч']:
        for abruptive_symbol in [
            '1', 'l', 'i', 'I', '|', 'ӏ',
            'І', 'I', 'I', 'ı', 'l', 'ɪ', 'ꟾ', 'ǀ',
            'Ι', 'ι', '|', '丨', 'ㅣ', 'ᛁ', 'ᛁ', '𐍘', '𐍭', 'Ⅰ'
        ]:
            text = text.replace(
                abruptive_letter+abruptive_symbol,
                abruptive_letter+PALOCHKA
            )
    return text


def fix_cp1252_encoding(text: str) -> str:
    char_list = list(text)
    for i in range(len(char_list)):
        try:
            char_list[i] = char_list[i].encode('cp1252').decode('cp1251')
        except UnicodeEncodeError:
            continue
    return ''.join(char_list)


lid_model = None


def is_lezgian(text: str, threshold: int = 0.8) -> bool:
    global lid_model

    if lid_model is None:
        model_path = hf_hub_download(
            repo_id="cis-lmu/glotlid",
            filename="model_v3.bin"
        )
        lid_model = fasttext.load_model(model_path)

    blacklist_labels = [
        '__label__rus_Cyrl',
        '__label__eng_Latn',
        '__label__azj_Latn',
        '__label__azj_Cyrl',
    ]
    labels, scores = lid_model.predict([text], k=3)

    label = labels[0][0]
    score = scores[0][0]

    if '__label__lez_Cyrl' in labels[0]:
        return True
    elif label not in blacklist_labels and score > threshold:
        return True

    return False


def has_cyrillic(text: str) -> bool:
    return bool(re.search('[А-Яа-я]', text))


def casing_errors_fix(text: str) -> str:
    """
    КьИЛИН редАКТордИН -> КЬИЛИН РЕДАКТОРДИН
    """
    fixed_tokens = list()
    for token in text.split():
        if PALOCHKA in token:
            t = token.replace(PALOCHKA, '')
        else:
            t = token

        if not (t.istitle() or t.islower() or t.isupper()):
            fixed_tokens.append(token.upper())
        else:
            fixed_tokens.append(token)

    return ' '.join(fixed_tokens)


def is_trash(text: str, min_tokens: int = 5) -> bool:
    text = text.replace('.', ' . ')
    tokens = word_tokenize(text)
    
    if len(tokens) < min_tokens:
        return True
    elif sum([not t.isalpha() for t in tokens]) / len(tokens) >= 0.5:
        return True
    elif sum([len(t) for t in tokens]) == len(tokens):
        return True
    elif np.mean([len(t) for t in tokens if t not in string.punctuation]) < 4:
        return True
    elif not has_cyrillic(text):
        return True

    return False


def is_poem(text: str) -> bool:
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    lines = text.splitlines()
    lines = [l.strip() for l in lines if l.strip() != '']

    if len(lines) < 8:
        return False

    percent_of_title_lines = sum([l[0].isupper() for l in lines]) / len(lines)
    percent_of_unique_endings = len(set([l[-2:] for l in lines])) / len(lines)
    mean_words_per_line = np.mean([len(l.split()) for l in lines])

    if (
        percent_of_title_lines > 0.8 and
        percent_of_unique_endings < 0.7 and
        3 < mean_words_per_line < 8
    ):
        return True

    return False
    


def tv_guide_classifier_regex(text: str) -> bool:
    if text.strip() == '':
        return False

    programm_hours = re.findall(
        r"\d{1,2}[.:]\d{2}",
        text,
        flags=re.MULTILINE
    )

    catch_words = [
        "теле",
        "телепрограмма",
        "домашний",
        "тв-центр",
        "ргвк",
        "нтв",
        "первый",
        "новост",
        "время",
        "х/ф",
        "д/ф",
        "м/с",
        "т/с",
        "шоу"
    ]
    count_of_catch_words = len(re.findall(
        f"({'|'.join(catch_words)})+",
        text.lower(),
        flags=re.MULTILINE&re.IGNORECASE
    ))

    if len(programm_hours) / len(text.splitlines()) > 1/4 or count_of_catch_words > 50:
        return True

    return False
        

def remove_url(text: str) -> str:
    return re.sub(
        r'https?://\S+|www\.\S+',
        '', text,
        flags=re.MULTILINE|re.IGNORECASE
    )


def remove_email_addresses(text: str) -> str:
    return re.sub(
        r'\S*@\S*\s?',
        '', text,
        flags=re.MULTILINE|re.IGNORECASE
    )


def remove_double_spaces(text: str) -> str:
    return re.sub(' +', ' ', text)


def remove_nonprintable_chars(text: str, respect_newline: bool = True) -> str:
    if respect_newline:
        lines = text.splitlines()
        return '\n'.join([
            remove_nonprintable_chars(l, False)
            for l in lines
        ])
    else:
        return ''.join([c for c in text if c.isprintable()])


def remove_emojis(text: str) -> str:
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text)


def remove_hyphens(text: str) -> str:
    """
    Source: https://pypdf.readthedocs.io/en/stable/user/post-processing-in-text-extraction.html#dehyphenation

    This fails for:
    * Natural dashes: well-known, self-replication, use-cases, non-semantic,
                      Post-processing, Window-wise, viewpoint-dependent
    * Trailing math operands: 2 - 4
    * Names: Lopez-Ferreras, VGG-19, CIFAR-100
    """
    lines = [line.rstrip() for line in text.split("\n")]

    # Find dashes
    line_numbers = []
    for line_no, line in enumerate(lines[:-1]):
        if line.endswith("-"):
            line_numbers.append(line_no)

    # Replace
    for line_no in line_numbers:
        lines = dehyphenate(lines, line_no)

    return "\n".join(lines)


def dehyphenate(lines: list[str], line_no: int) -> list[str]:
    """
    Source: https://pypdf.readthedocs.io/en/stable/user/post-processing-in-text-extraction.html#dehyphenation
    """
    next_line = lines[line_no + 1]
    word_suffix = next_line.split(" ")[0]

    lines[line_no] = lines[line_no][:-1] + word_suffix
    lines[line_no + 1] = lines[line_no + 1][len(word_suffix) :]
    return lines