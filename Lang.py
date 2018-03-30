SOS_token = 0
EOS_token = 1

class Lang:
	def __init__(self, name):
		self.name = name
		self.word2index = {}
		self.index2word = {0: "SOS", 1: "EOS"}
		self.word2count = {}
		self.n_words = 2	# total number of words; SOS=0 and EOS=1 already counted

	def addWord(self, word):
		if word not in self.word2index:
			self.word2index[word] = self.n_words
			self.word2count[word] = 1
			self.index2word[self.n_words] = word
			self.n_words += 1
		else:
			self.word2count[word] += 1

	def addSentence(self, sentence):
		for word in sentence.split(' '):
			self.addWord(word)