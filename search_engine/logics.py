from .models import *

from Bio import Entrez, Medline
from pathlib import Path
import sys, time

# Get_core.main import main as bert_prediction
path_to_bert = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'BERT_core'))
sys.path.append(path_to_bert)

from BERT_core.main import result_list_drugs as bert_prediction


class Analise_record:
    """Делаем таск который применяет документ,
    проверяет его на наличие в бд если нет то обрабатываем Bert
    и потом сохраняем в бд"""
    def __init__(self, _record, _query_task):
        self.record = _record
        self.query_task = _query_task

    def ahalise_doc(self):
        """Получаем документ, проверяем в бд а потом загружаем в берт и выводим информацию"""
        try:
            rec_id = self.record['PMID']
        except:
            rec_id = self.record['PMC'][3:]
        if self.check_in_database(rec_id):
            message = f'Документ под номером {rec_id} уже добавлен в базу данных'
            data = None
        else:
            self.prepare_text()
            try:
                drug_doc = bert_prediction(rec_id, self.record['TI'], self.record['AB'])
            except:
                message = f'Произошла ошибка при обработке документа под номером {rec_id}'
                data = None
                return message, data

            len_drug_doc, count_append = self.append_in_database(drug_doc)

            print(f'Из {len_drug_doc} обработанных Bert добавили в бд {count_append}')

            if count_append != 0.0:  # Проверяем на кол-во добавленных
                append = True
            else:
                append = False
            message, data = self.create_message(append, rec_id)
        return message, data

    def check_in_database(self, rec_id):
        """Проверям на наличие в локальной бд, если есть то False если нет то True"""
        if DdiFact.objects.filter(id_doc=rec_id).exists():
            time.sleep(2)
            return True
        else:
            return False

    def prepare_text(self):
        """Проверяем документ на валидность"""
        try:  # Проверяем есть ли заголовок
            self.record['TI'] = str(self.record['TI'])
        except:
            self.record['TI'] = '.'

        try:  # Проверяем есть ли основной текст
            self.record['AB'] = str(self.record['AB'])
        except:
            self.record['AB'] = '.'
        self.record['AB'] = self.record['TI'] + self.record['AB']

    def append_in_database(self, drug_doc):
        """Проходим по файлам обработаных Бертом и добавляем где есть иттерации"""
        count_add = 0
        for drug in drug_doc:
            print(drug['ddi_type'])
            if drug['ddi_type'] != "No_interaction":  # если типа взаимодействия нет то не сохраняем
                count_add += 1
                ddi = self.append_DdiFact(drug)  # сохраняем предложение в локальную бд
                for i in drug['drugs']:  # Циклом сохраняем все ссылки на препараты в этом предложении в локальную бд
                    self.append_Drug(i, ddi)
        return len(drug_doc), count_add

    def append_DdiFact(self, drug):
        """Добавляем в бд взаимодействие"""
        ddi = DdiFact(
            id_task=self.query_task,
            id_doc=drug['id_doc'],
            sentence_txt=drug['sentence_txt'],
            parsing_txt=drug['parsing_txt'],
            numb_sentence_in_doc=drug['numb_sentence_in_doc'],
            ddi_type=drug['ddi_type']
        )
        ddi.save()
        return ddi

    def append_Drug(self, drug, ddi):
        """Добавляем препараты которые участвовали в взаимодействии"""
        drug = DrugLink(
            id_fact=ddi,
            drug_name=drug
        )
        drug.save()

    def create_message(self, append, rec_id):
        if append is False:
            result_string = f'В документе под номером {rec_id} не найдено взаимодействий'
            data = None
        else:
            result_string = f'Документ под номером {rec_id} успешно обработался'
            try:
                title_pres = self.record['TI'][:100]
            except:
                title_pres = self.record['TI']

            try:  # Проверяем если ли главный автор
                author = self.record['AU'][0]
            except:
                author = 'None define'

            try:  # Проверяем есть ли место публикации
                place = self.record['AD'][0]
            except:
                place = 'None define'

            data = {'PMID': rec_id,
                    'title': title_pres,
                    'author': author,
                    'place': place}  # Получаем данные если есть и выводим в виде таблицы
        return result_string, data


def get_global_data(email, source, search_str):
    """Получение записей для группового выполнения"""
    Entrez.email = email  # Майл пользователя
    handle = Entrez.esearch(db=source, sort='relevance', term=search_str, retmax='10000')
    record = Entrez.read(handle)
    rec_count = record['Count']  # Кол-во найденных записей
    print(search_str, ' - ', rec_count)


    idlist = record["IdList"]
    handle = Entrez.efetch(db=source, id=idlist, rettype="medline", retmode="text")
    records = Medline.parse(handle)
    records_const = [record for record in records]
    return records_const, rec_count






