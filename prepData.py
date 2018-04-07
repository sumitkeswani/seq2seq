import utils
import filterData
import random

def prepareData():
	input_lang, output_lang, pairs = utils.readLangs()
	print("Read %s sentence pairs" % len(pairs))
	pairs = filterData.filterPairs(pairs)
	print("Trimmed to %s sentence pairs" % len(pairs))
	print("Counting words...")
	for pair in pairs:
		input_lang.addSentence(pair[0])
		output_lang.addSentence(pair[1])
	print("Counted words:")
	print(input_lang.name, input_lang.n_words)
	print(output_lang.name, output_lang.n_words)
	return input_lang, output_lang, pairs

input_lang, output_lang, pairs = prepareData()

print(random.choice(pairs))
