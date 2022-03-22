from bert import Bert


# BERT_core-RE model for finding
# interactions between drugs
class ReBert(Bert):
    def __init__(self, device, model, tokenizer, labels_dictionary):
        super().__init__(device, model, tokenizer, labels_dictionary)

    def get_predictions(self, batched_array):
        predictions = []
        for batch in batched_array:
            prediction = self.get_prediction_for_batch(batch)
            predictions.append(prediction)
        return predictions

    # Return prediction for the batch
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
        result_interactions = self.get_predicted_interactions(prediction_list)
        return result_interactions

    # Return prediction in the words:
    # 'No_interaction' or 'effect' or 'advise' or ...
    # by RElables.json
    def get_predicted_interactions(self, interactions_predicted_list):
        return super().get_predicted_class(interactions_predicted_list)
