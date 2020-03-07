from ragde import readability
from ragde.filing_readability import _filing_readability

text = "I am a modern model of a modern major general"
def test___get_lang_easy_words():
    easy_word_set = {ln.decode("utf-8").strip() for ln in open('easy_words.txt', 'rb').readlines()}
    assert readability.__get_lang_easy_words() == easy_word_set, 'Easy words fails'
    
def test_difficult_words():
    assert readability.difficult_words(text) == 2, 'Difficult words fails'
    
def test_avg_character_per_word():
    assert readability.avg_character_per_word(text) == 3.6, 'Avg character per word fails'
    
def test__filing_readability():
    assert _filing_readability('1001039', 2011, output_file = "", filing_type="10K", verbose=True) == 0, 'Filing readability (single) fails'

if __name__ == "__main__":
    test___get_lang_easy_words()
    test_difficult_words(text)
    test_avg_character_per_word(text)
    print("Everything passed")