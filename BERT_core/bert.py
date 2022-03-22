class Bert:
    def __init__(self, device, model, tokenizer, labels_dictionary):
        self.device = device
        self.model = model
        self.tokenizer = tokenizer
        self.labels_dictionary = labels_dictionary

    # The function that predicts class (interaction or drug) in list
    # from json file
    def get_predicted_class(self, prediction_list):
        text_classes = list(self.labels_dictionary.keys())
        predicted_classes = []
        for word_predictions in prediction_list:
            index_of_max_element = word_predictions.index(max(word_predictions))
            predicted_classes.append(text_classes[index_of_max_element])
        return predicted_classes
