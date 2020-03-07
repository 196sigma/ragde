import readability
import filing_readability

text = "I am a modern model of a modern major general"

def test_difficult_words():
    assert readability.difficult_words(text) == 2, 'Difficult words fails'
    
def test_avg_character_per_word():
    assert readability.avg_character_per_word(text) == 3.6, 'Avg character per word fails'
    
def test__filing_readability():
    assert _filing_readability('1001039', 2011, output_file = "", filing_type="10K", verbose=True), 0

if __name__ == "__main__":

    test_difficult_words(text)
    test_avg_character_per_word(text)
    print("Everything passed")