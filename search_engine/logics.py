from .models import DdiFact, DdiDocument, Author, Place, DrugLink

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

            len_drug_doc, count_append = self.append_in_database(drug_doc, rec_id)

            print(f'Из {len_drug_doc} обработанных Bert добавили в бд {count_append}')

            if count_append != 0.0:  # Проверяем на кол-во добавленных
                append = True
            else:
                append = False
            message, data = self.create_message(append, rec_id)
        return message, data

    def check_in_database(self, rec_id):
        """Проверям на наличие в локальной бд, если есть то False если нет то True"""
        if DdiDocument.objects.filter(id_record=rec_id).exists():
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

    def append_in_database(self, drug_doc, rec_id):
        """Проходим по файлам обработаных Бертом и добавляем где есть иттерации"""
        count_add = 0
        if self.check_count_effects(drug_doc):
            return len(drug_doc), count_add
        else:
            ddi_doc = self.append_DdiDoc(rec_id)
            self.append_authors(ddi_doc)
            self.append_places(ddi_doc)
            for drug in drug_doc:
                print(drug['ddi_type'])
                if drug['ddi_type'] != "No_interaction":  # если типа взаимодействия нет то не сохраняем
                    count_add += 1
                    ddi = self.append_DdiFact(drug, ddi_doc)  # сохраняем предложение в локальную бд
                    for i in drug['drugs']:  # Циклом сохраняем все ссылки на препараты в этом предложении в локальную бд
                        self.append_Drug(i, ddi)
        return len(drug_doc), count_add

    def check_count_effects(self, drug_dict):
        """Проверяем текст на наличие взаимодействий"""
        for drug in drug_dict:
            if drug['ddi_type'] != "No_interaction":
                return False
        return True

    def append_DdiDoc(self, rec_id):
        """Добавляем документ в бд с номером записи и кол-вом добалвенных предложений"""
        ddi_doc = DdiDocument(
            task_query=self.query_task,
            id_record=rec_id,
            title=self.record['TI']
        )
        ddi_doc.save()
        return ddi_doc

    def append_authors(self, ddi_doc):
        """Добавляем авторов статьи"""
        try:
            authors = self.record['AU']
        except:
            authors = None
        if authors:
            for author_name in authors:
                if Author.objects.filter(name_author=author_name).count() > 1:
                    author = Author.objects.filter(name_author=author_name)[0]
                else:
                    author = Author.objects.get_or_create(name_author=author_name)[0]
                ddi_doc.authors.add(author)

    def append_places(self, ddi_doc):
        """Добавляем места исследования"""
        try:
            places = self.record['AD']
        except:
            places = None
        if places:
            for place_str in places:
                exist_place = Place.objects.filter(place_research=place_str)
                if exist_place.count() > 1:
                    place = exist_place[0]
                elif exist_place.count() == 1.0:
                    place = Place.objects.get(place_research=place_str)
                elif exist_place.count() == 0.0:
                    place = Place.objects.create(place_research=place_str)
                ddi_doc.places.add(place)


    def append_DdiFact(self, drug, ddi_doc):
        """Добавляем в бд взаимодействие"""
        ddi = DdiFact(
            id_doc=ddi_doc,
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


class Place_dict(dict):
    """Словарь для сохранения данных о месте исследования"""


