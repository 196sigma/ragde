import warnings
import string
import re
import math
import pkg_resources
from collections import Counter
from functools import lru_cache
from pyphen import Pyphen

langs = {
    "en": {  # Default config
        "fre_base": 206.835,
        "fre_sentence_length": 1.015,
        "fre_syll_per_word": 84.6,
        "syllable_threshold": 3,
    }
}

__lang = "en_US"
text_encoding = "utf-8"

def legacy_round(number, points=0):
    p = 10 ** points
    return float(math.floor((number * p) + math.copysign(0.5, number))) / p

def get_grade_suffix(grade):
    """
    Select correct ordinal suffix
    """
    ordinal_map = {1: 'st', 2: 'nd', 3: 'rd'}
    teens_map = {11: 'th', 12: 'th', 13: 'th'}
    return teens_map.get(grade % 100, ordinal_map.get(grade % 10, 'th'))

def _cache_clear(self):
    caching_methods = [
        method for method in dir(self)
        if callable(getattr( method))
        and hasattr(getattr( method), "cache_info")
    ]

    for method in caching_methods:
        getattr( method).cache_clear()

@lru_cache(maxsize=128)
def char_count( text, ignore_spaces=True):
    """
    Function to return total character counts in a text,
    pass the following parameter `ignore_spaces = False`
    to ignore whitespaces
    """
    if ignore_spaces:
        text = text.replace(" ", "")
    return len(text)

@lru_cache(maxsize=128)
def letter_count( text, ignore_spaces=True):
    """
    Function to return total letter amount in a text,
    pass the following parameter `ignore_spaces = False`
    to ignore whitespaces
    """
    if ignore_spaces:
        text = text.replace(" ", "")
    return len(remove_punctuation(text))

def remove_punctuation(text):
    return ''.join(ch for ch in text if ch not in string.punctuation)

@lru_cache(maxsize=128)
def lexicon_count( text, removepunct=True):
    """
    Function to return total lexicon (words in lay terms) counts in a text
    """
    if removepunct:
        text = remove_punctuation(text)
    count = len(text.split())
    return count

@lru_cache(maxsize=128)
def syllable_count( text, lang=None):
    """
    Function to calculate syllable words in a text.
    I/P - a text
    O/P - number of syllable words
    """

    if isinstance(text, bytes):
        text = text.decode(text_encoding)

    text = text.lower()
    text = remove_punctuation(text)

    if not text:
        return 0

    dic = Pyphen(lang=__lang)
    count = 0
    for word in text.split(' '):
        word_hyphenated = dic.inserted(word)
        count += max(1, word_hyphenated.count("-") + 1)
    return count

@lru_cache(maxsize=128)
def sentence_count( text):
    """
    Sentence count of a text
    """
    ignore_count = 0
    sentences = re.split(r' *[\.\?!][\'"\)\]]*[ |\n](?=[A-Z])', text)
    for sentence in sentences:
        if lexicon_count(sentence) <= 2:
            ignore_count += 1
    return max(1, len(sentences) - ignore_count)

@lru_cache(maxsize=128)
def avg_sentence_length( text):
    try:
        asl = float(lexicon_count(text) / sentence_count(text))
        return legacy_round(asl, 1)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def avg_syllables_per_word( text, interval=None):
    syllable = syllable_count(text)
    words = lexicon_count(text)
    try:
        if interval:
            syllables_per_word = float(syllable) * interval / float(words)
        else:
            syllables_per_word = float(syllable) / float(words)
        return legacy_round(syllables_per_word, 1)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def avg_character_per_word( text):
    try:
        letters_per_word = float(
            char_count(text) / lexicon_count(text))
        return legacy_round(letters_per_word, 2)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def avg_letter_per_word( text):
    try:
        letters_per_word = float(
            letter_count(text) / lexicon_count(text))
        return legacy_round(letters_per_word, 2)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def avg_sentence_per_word( text):
    try:
        sentence_per_word = float(
            sentence_count(text) / lexicon_count(text))
        return legacy_round(sentence_per_word, 2)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def flesch_reading_ease( text):
    sentence_length = avg_sentence_length(text)
    s_interval = 100 if __get_lang_root() in ['es', 'it'] else None
    syllables_per_word = avg_syllables_per_word(text, s_interval)
    flesch = (
        __get_lang_cfg("fre_base")
        - float(
            __get_lang_cfg("fre_sentence_length") * sentence_length
        )
        - float(
            __get_lang_cfg("fre_syll_per_word") * syllables_per_word
        )
    )
    return legacy_round(flesch, 2)

@lru_cache(maxsize=128)
def flesch_kincaid_grade( text):
    sentence_lenth = avg_sentence_length(text)
    syllables_per_word = avg_syllables_per_word(text)
    flesch = (
            float(0.39 * sentence_lenth)
            + float(11.8 * syllables_per_word)
            - 15.59)
    return legacy_round(flesch, 1)

@lru_cache(maxsize=128)
def polysyllabcount( text):
    count = 0
    for word in text.split():
        wrds = syllable_count(word)
        if wrds >= 3:
            count += 1
    return count

@lru_cache(maxsize=128)
def smog_index( text):
    sentences = sentence_count(text)

    if sentences >= 3:
        try:
            poly_syllab = polysyllabcount(text)
            smog = (
                    (1.043 * (30 * (poly_syllab / sentences)) ** .5)
                    + 3.1291)
            return legacy_round(smog, 1)
        except ZeroDivisionError:
            return 0.0
    else:
        return 0.0

@lru_cache(maxsize=128)
def coleman_liau_index( text):
    letters = legacy_round(avg_letter_per_word(text) * 100, 2)
    sentences = legacy_round(avg_sentence_per_word(text) * 100, 2)
    coleman = float((0.058 * letters) - (0.296 * sentences) - 15.8)
    return legacy_round(coleman, 2)

@lru_cache(maxsize=128)
def automated_readability_index( text):
    chrs = char_count(text)
    words = lexicon_count(text)
    sentences = sentence_count(text)
    try:
        a = float(chrs) / float(words)
        b = float(words) / float(sentences)
        readability = (
                (4.71 * legacy_round(a, 2))
                + (0.5 * legacy_round(b, 2))
                - 21.43)
        return legacy_round(readability, 1)
    except ZeroDivisionError:
        return 0.0

#@lru_cache(maxsize=128)
def linsear_write_formula( text):
    easy_word = 0
    difficult_word = 0
    text_list = text.split()[:100]

    for word in text_list:
        if syllable_count(word) < 3:
            easy_word += 1
        else:
            difficult_word += 1

    text = ' '.join(text_list)

    number = float(
        (easy_word * 1 + difficult_word * 3)
        / sentence_count(text))

    if number <= 20:
        number -= 2

    return number / 2

#@lru_cache(maxsize=128)
def difficult_words( text, syllable_threshold=2):
    return len(difficult_words_list(text, syllable_threshold))

#@lru_cache(maxsize=128)
def difficult_words_list( text, syllable_threshold=2):
    text_list = re.findall(r"[\w\='‘’]+", text.lower())
    diff_words_set = set()
    easy_word_set = __get_easy_words()
    for value in text_list:
        if value not in easy_word_set:
            if syllable_count(value) >= syllable_threshold:
                diff_words_set.add(value)
    return list(diff_words_set)


@lru_cache(maxsize=128)
def gunning_fog( text):
    try:
        syllable_threshold = __get_lang_cfg("syllable_threshold")
        per_diff_words = (
            difficult_words(
                text,
                syllable_threshold=syllable_threshold)
            / lexicon_count(text) * 100)

        grade = 0.4 * (avg_sentence_length(text) + per_diff_words)
        return legacy_round(grade, 2)
    except ZeroDivisionError:
        return 0.0

@lru_cache(maxsize=128)
def lix( text):
    words = text.split()

    words_len = len(words)
    long_words = len([wrd for wrd in words if len(wrd) > 6])

    per_long_words = (float(long_words) * 100) / words_len
    asl = avg_sentence_length(text)
    lix = asl + per_long_words

    return legacy_round(lix, 2)

@lru_cache(maxsize=128)
def rix( text):
    """
    A Rix ratio is simply the number of long words divided by
    the number of assessed sentences.
    rix = LW/S
    """
    words = text.split()
    long_words_count = len([wrd for wrd in words if len(wrd) > 6])
    sentences_count = sentence_count(text)

    try:
        rix = long_words_count / sentences_count
    except ZeroDivisionError:
        rix = 0.00

    return legacy_round(rix, 2)

@lru_cache(maxsize=128)
def spache_readability( text, float_output=True):
    """
    Function to calculate SPACHE readability formula for young readers.
    I/P - a text
    O/P - an int Spache Readability Index/Grade Level
    """
    total_no_of_words = lexicon_count(text)
    count_of_sentences = sentence_count(text)
    asl = total_no_of_words / count_of_sentences
    pdw = (difficult_words(text) / total_no_of_words) * 100
    spache = (0.141 * asl) + (0.086 * pdw) + 0.839
    if not float_output:
        return int(spache)
    else:
        return spache

@lru_cache(maxsize=128)
def dale_chall_readability_score_v2( text):
    """
    Function to calculate New Dale Chall Readability formula.
    I/P - a text
    O/P - an int Dale Chall Readability Index/Grade Level
    """
    total_no_of_words = lexicon_count(text)
    count_of_sentences = sentence_count(text)
    asl = total_no_of_words / count_of_sentences
    pdw = (difficult_words(text) / total_no_of_words) * 100
    raw_score = 0.1579 * (pdw) + 0.0496 * asl
    adjusted_score = raw_score
    if raw_score > 0.05:
        adjusted_score = raw_score + 3.6365
    return legacy_round(adjusted_score, 2)

@lru_cache(maxsize=128)
def text_standard( text, float_output=None):

    grade = []

    # Appending Flesch Kincaid Grade
    lower = legacy_round(flesch_kincaid_grade(text))
    upper = math.ceil(flesch_kincaid_grade(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Flesch Reading Easy
    score = flesch_reading_ease(text)
    if score < 100 and score >= 90:
        grade.append(5)
    elif score < 90 and score >= 80:
        grade.append(6)
    elif score < 80 and score >= 70:
        grade.append(7)
    elif score < 70 and score >= 60:
        grade.append(8)
        grade.append(9)
    elif score < 60 and score >= 50:
        grade.append(10)
    elif score < 50 and score >= 40:
        grade.append(11)
    elif score < 40 and score >= 30:
        grade.append(12)
    else:
        grade.append(13)

    # Appending SMOG Index
    lower = legacy_round(smog_index(text))
    upper = math.ceil(smog_index(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Coleman_Liau_Index
    lower = legacy_round(coleman_liau_index(text))
    upper = math.ceil(coleman_liau_index(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Automated_Readability_Index
    lower = legacy_round(automated_readability_index(text))
    upper = math.ceil(automated_readability_index(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Dale_Chall_Readability_Score
    lower = legacy_round(dale_chall_readability_score_v2(text))
    upper = math.ceil(dale_chall_readability_score_v2(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Linsear_Write_Formula
    lower = legacy_round(linsear_write_formula(text))
    upper = math.ceil(linsear_write_formula(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Appending Gunning Fog Index
    lower = legacy_round(gunning_fog(text))
    upper = math.ceil(gunning_fog(text))
    grade.append(int(lower))
    grade.append(int(upper))

    # Finding the Readability Consensus based upon all the above tests
    d = Counter(grade)
    final_grade = d.most_common(1)
    score = final_grade[0][0]

    if float_output:
        return float(score)
    else:
        lower_score = int(score) - 1
        upper_score = lower_score + 1
        return "{}{} and {}{} grade".format(
            lower_score, get_grade_suffix(lower_score),
            upper_score, get_grade_suffix(upper_score)
        )

@lru_cache(maxsize=128)
def reading_time( text, ms_per_char=14.69):
    """
    Function to calculate reading time (Demberg & Keller, 2008)
    I/P - a text
    O/P - reading time in second
    """
    words = text.split()
    nchars = map(len, words)
    rt_per_word = map(lambda nchar: nchar * ms_per_char, nchars)
    reading_time = sum(list(rt_per_word))

    return legacy_round(reading_time/1000, 2)

def __get_lang_cfg( key):
    default = langs.get("en")
    config = langs.get(__get_lang_root(), default)
    return config.get(key, default.get(key))

def __get_lang_root():
    return __lang.split("_")[0]

def __get_easy_words():
    try:
        easy_word_set = {ln.decode("utf-8").strip() for ln in pkg_resources.resource_stream("ragde","easy_words.txt")}
        #easy_word_set = {ln.decode("utf-8").strip() for ln in open('easy_words.txt', 'rb').readlines()}
    except FileNotFoundError:
        print("There is no easy words vocabulary.")
        return
    return easy_word_set