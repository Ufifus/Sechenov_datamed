import torch
import json
from transformers import BertForTokenClassification, BertForSequenceClassification
from transformers import BertTokenizer
from ner_bert import NerBert
from re_bert import ReBert
from os import path
from nltk import tokenize
import re

import nltk

nltk.download('punkt')

path_to_BERT = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'BERT_core')


def main(text):
    sentences = preparation_for_prediction(text, batch_size=10)
    initialized_ner = ner_initialization()
    initialized_re = re_initialization()
    ner_model = NerBert(*initialized_ner)
    sentences_after_ner, tokens_count_list, drugs_list = ner_model.get_predictions(sentences)
    re_model = ReBert(*initialized_re)
    re_interaction = re_model.get_predictions(sentences_after_ner)
    return sentences, sentences_after_ner, tokens_count_list, re_interaction, drugs_list


# NER-BERT initialization
def ner_initialization():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    path_to_bert_ner = str(path.join(path_to_BERT, 'NER5'))
    model = BertForTokenClassification.from_pretrained(path_to_bert_ner)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    path_to_labels_dict = str(path.join(path_to_BERT, 'labels_dictionary.json'))
    with open(path_to_labels_dict) as json_file:
        labels_dictionary = json.load(json_file)
    model.to(device)
    model.eval()
    return device, model, tokenizer, labels_dictionary


# RE-BERT initialization
def re_initialization():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    path_to_bert_re = str(path.join(path_to_BERT, 'Bert_med_re_v5_cont_ep_3'))
    model = BertForSequenceClassification.from_pretrained(path_to_bert_re)
    path_to_medtokenizer = str(path.join(path_to_BERT, 'MEDtokenizer'))
    tokenizer = BertTokenizer.from_pretrained(path_to_medtokenizer)
    path_to_relabels = str(path.join(path_to_BERT, 'RElabels.json'))
    with open(path_to_relabels) as json_file:
        labels_dictionary = json.load(json_file)
    model.to(device)
    model.eval()
    return device, model, tokenizer, labels_dictionary


# The function that returns list of batched sentences
# with whitespaces between words
def preparation_for_prediction(text, batch_size):
    batch_list = []
    batch = []
    for sentence in tokenize.sent_tokenize(text):
        cleared_sentence = ' '.join(re.findall(r"[A-Za-z@#]+|\S", sentence))
        batch.append(cleared_sentence)
        if len(batch) > batch_size:
            batch_list.append(batch)
            batch = []
    if len(batch) != 0:
        batch_list.append(batch)
    return batch_list


# Return result list of texts with predicted labels and interactions
def result_list(id, title, sentences_before_ner, sentences_after_ner, tokens_count, re_interactions, drugs_list):
    answer_list = []
    for i, batch in enumerate(sentences_before_ner):
        for j, sentence in enumerate(batch):
            if tokens_count[i][j] > 0:
                sentence_dict = {
                    'id_doc': id,
                    'title_doc': title,
                    'sentence_txt': sentence,
                    'parsing_txt': sentences_after_ner[i][j],
                    'ddi_type': re_interactions[i][j],
                    'numb_sentence_in_doc': j + 1,
                    'drugs': drugs_list[i][j]
                }
                answer_list.append(sentence_dict)
    return answer_list

def result_list_drugs(id, title, text):  # Ф-я для загрузки в Bert на выходе получаем массив предложений
    return result_list(id, title, *main(text))