def indexesFromSentence(lang, sentence):
	return [lang.word2index[word] for word in sentence.split(' ')]


def variableFromSentence(lang, sentence):
	indexes = indexesFromSentence(lang, sentence)
	indexes.append(EOS_token)
	result = Variable(torch.LongTensor(indexes).view(-1, 1))
	if use_cuda:
		return result.cuda()
	else:
		return result


def variablesFromPair(pair):
	input_variable = variableFromSentence(input_lang, pair[0])
	target_variable = variableFromSentence(output_lang, pair[1])
	return (input_variable, target_variable)