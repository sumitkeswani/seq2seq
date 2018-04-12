class EncoderRNN(nn.Module):
	def __init__(self, input_size, hidden_size):
		super(EncoderRNN, self).__init__()
		self.hidden_size = hidden_size

		self.embedding = nn.Embedding(input_size, hidden_size)
		self.gru = nn.GRU(hidden_size, hidden_size)

	def forward(self, input, hidden):
		embedded = self.embedding(input).view(1, 1, -1)
		output = embedded
		output, hidden = self.gru(output, hidden)
		return output, hidden

	def initHidden(self):
		result = Variable(torch.zeros(1, 1, self.hidden_size))
		if use_cuda:
			return result.cuda()
		else:
			return result


class AttnDecoderRNN(nn.Module):
	def __init__(self, hidden_size, output_size, dropout_p=0.1, max_length=MAX_LENGTH):
		super(AttnDecoderRNN, self).__init__()
		self.hidden_size = hidden_size
		self.output_size = output_size
		self.dropout_p = dropout_p
		self.max_length = max_length

		self.embedding = nn.Embedding(self.output_size, self.hidden_size)
		self.attn = nn.Linear(self.hidden_size * 2, self.max_length)
		self.attn_combine = nn.Linear(self.hidden_size * 2, self.hidden_size)
		self.dropout = nn.Dropout(self.dropout_p)
		self.gru = nn.GRU(self.hidden_size, self.hidden_size)
		self.out = nn.Linear(self.hidden_size, self.output_size)

	def forward(self, input, hidden, encoder_outputs):
		embedded = self.embedding(input).view(1, 1, -1)
		embedded = self.dropout(embedded)

		attn_weights = F.softmax(
			self.attn(torch.cat((embedded[0], hidden[0]), 1)), dim=1)
		attn_applied = torch.bmm(attn_weights.unsqueeze(0),
								 encoder_outputs.unsqueeze(0))

		output = torch.cat((embedded[0], attn_applied[0]), 1)
		output = self.attn_combine(output).unsqueeze(0)

		output = F.relu(output)
		output, hidden = self.gru(output, hidden)

		output = F.log_softmax(self.out(output[0]), dim=1)
		return output, hidden, attn_weights

	def initHidden(self):
		result = Variable(torch.zeros(1, 1, self.hidden_size))
		if use_cuda:
			return result.cuda()
		else:
			return result

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

teacher_forcing_ratio = 0.5


def train(input_variable, target_variable, encoder, decoder, encoder_optimizer, decoder_optimizer, criterion, max_length=MAX_LENGTH):
	encoder_hidden = encoder.initHidden()

	encoder_optimizer.zero_grad()
	decoder_optimizer.zero_grad()

	input_length = input_variable.size()[0]
	target_length = target_variable.size()[0]

	encoder_outputs = Variable(torch.zeros(max_length, encoder.hidden_size))
	encoder_outputs = encoder_outputs.cuda() if use_cuda else encoder_outputs

	loss = 0

	for ei in range(input_length):
		encoder_output, encoder_hidden = encoder(
			input_variable[ei], encoder_hidden)
		encoder_outputs[ei] = encoder_output[0][0]

	decoder_input = Variable(torch.LongTensor([[SOS_token]]))
	decoder_input = decoder_input.cuda() if use_cuda else decoder_input

	decoder_hidden = encoder_hidden

	use_teacher_forcing = True if random.random() < teacher_forcing_ratio else False

	if use_teacher_forcing:
		# Teacher forcing: Feed the target as the next input
		for di in range(target_length):
			decoder_output, decoder_hidden, decoder_attention = decoder(
				decoder_input, decoder_hidden, encoder_outputs)
			loss += criterion(decoder_output, target_variable[di])
			decoder_input = target_variable[di]  # Teacher forcing

	else:
		# Without teacher forcing: use its own predictions as the next input
		for di in range(target_length):
			decoder_output, decoder_hidden, decoder_attention = decoder(
				decoder_input, decoder_hidden, encoder_outputs)
			topv, topi = decoder_output.data.topk(1)
			ni = topi[0][0]

			decoder_input = Variable(torch.LongTensor([[ni]]))
			decoder_input = decoder_input.cuda() if use_cuda else decoder_input

			loss += criterion(decoder_output, target_variable[di])
			if ni == EOS_token:
				break

	loss.backward()

	encoder_optimizer.step()
	decoder_optimizer.step()

	return loss.data[0] / target_length


def asMinutes(s):
	m = math.floor(s / 60)
	s -= m * 60
	return '%dm %ds' % (m, s)


def timeSince(since, percent):
	now = time.time()
	s = now - since
	es = s / (percent)
	rs = es - s
	return '%s (- %s)' % (asMinutes(s), asMinutes(rs))

