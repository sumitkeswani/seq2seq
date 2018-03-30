import Lang
import unicodedata
import re

# Turn a Unicode string to plain ASCII, thanks to
# http://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

# Lowercase, trim, and remove non-letter characters


def normalizeString(s):
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
    return s

def readLangs():
	print("reading languages...")

	lines = open("data/eng-fra.txt", encoding='utf-8').read().strip().split('\n')

	pairs = [[normalizeString(s) for s in l.split('\t')] for l in lines]

	input_lang = Lang.Lang("eng")
	output_lang = Lang.Lang("fra")

	return input_lang, output_lang, pairs
