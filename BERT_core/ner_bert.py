from bert import Bert


# NER Bert model for finding
# drugs in texts
class NerBert(Bert):
    def __init__(self, device, model, tokenizer, labels_dictionary):
        super().__init__(device, model, tokenizer, labels_dictionary)

    # Predict function for all texts
    def get_predictions(self, batched_array):
        predicted_sentences = []
        tokens_count_list = []
        drugs_in_sentences = []
        for batch in batched_array:
            tokens_for_sentences = self.get_prediction_for_batch(batch)
            sentences_with_tokens, \
            tokens_count, \
            drugs_list = self.import_tokens_into_sentences(batch, tokens_for_sentences)
            predicted_sentences.append(sentences_with_tokens)
            tokens_count_list.append(tokens_count)
            drugs_in_sentences.append(drugs_list)
        return predicted_sentences, tokens_count_list, drugs_in_sentences

    # Predict labels for the one batch
    def get_prediction_for_batch(self, batch):
        tokenizer_dict = self.tokenizer(
            batch,
            return_tensors='pt',
            padding=True,
            truncation=True,
            is_split_into_words=False,
            max_length=512).to(self.device)
        classifier_outputs = self.model(**tokenizer_dict)
        prediction_list = classifier_outputs.logits.tolist()
        result_prediction = []
        for i, label_predictions in enumerate(prediction_list):
            decoded_words = self.get_decoded_words(tokenizer_dict['input_ids'].tolist()[i])
            predicted_tokens = self.get_predicted_tokens(label_predictions)
            tokens = self.tokens_filter(decoded_words, predicted_tokens)
            result_prediction.append(tokens)
        return result_prediction

    # Checks decoded subword for a token
    # and return boolean
    def is_not_special_token(self, subword):
        tokens_list = ['[ C L S ]',
                       '# #',
                       '[ S E P ]',
                       '[ P A D ]']
        if subword[0:3] in tokens_list or subword in tokens_list:
            return False
        return True

    # Function that gets the list of tokens
    # and returns the list of decoded words
    def get_decoded_words(self, tokens_list):
        decoded_words = []
        for token in tokens_list:
            decoded_words.append(self.tokenizer.decode(token))
        return decoded_words

    # Gets prediction list from BERT_core model
    # and returns predicted labels by labels dictionary
    def get_predicted_tokens(self, token_predictions):
        return super().get_predicted_class(token_predictions)

    # Return lists of words without tokens,
    # such as: [ C L S ], # #, [ S E P ], [ P A D ]
    def tokens_filter(self, decoded_words, predicted_tokens):
        tokens = []
        for subword, token in zip(decoded_words, predicted_tokens):
            if self.is_not_special_token(subword):
                # Changes name of token to readable
                # Example: B-DRUG -> DRUG
                if token != '-':
                    token = token[2:]
                tokens.append(token)
        return tokens

    # Import predicted tokens in sentences and returns
    def import_tokens_into_sentences(self, sentences, tokens_list):
        sentences_with_tokens = []
        tokens_count_list = []
        drugs_in_text = []
        for i, sentence in enumerate(sentences):
            new_sentence = []
            tokens_count = 0
            drugs_in_sentence = []
            for j, word in enumerate(sentence.split()):
                if tokens_list[i][j] != '-':
                    tokens_count += 1
                    if tokens_list[i][j] == 'DRUG':
                        drugs_in_sentence.append(word)
                    new_sentence.append(f'[{word} --- {tokens_list[i][j]}]')
                else:
                    new_sentence.append(word)
            drugs_in_text.append(drugs_in_sentence)
            sentences_with_tokens.append(' '.join(new_sentence))
            tokens_count_list.append(tokens_count)
        return sentences_with_tokens, tokens_count_list, drugs_in_text
