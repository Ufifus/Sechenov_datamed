from .models import *
from django_celery_results.models import TaskResult
from django.contrib.auth.models import User


from BERT_core.main import result_list_drugs as bert_prediction


from Bio import Entrez, Medline
from sentence_splitter import SentenceSplitter, split_text_into_sentences


# Get_core.main import main as bert_prediction


# Обрабатываем документ Bert
def analise_doc(doc, query_task):
    drug_dict = bert_prediction(*doc)  # пропускаем документ через бд
    j = 0
    for drug in drug_dict:
        print(drug['ddi_type'])
        if drug['ddi_type'] != "No_interaction":  # если типа взаимодействия нет то не сохраняем если есть то сохраняем
            j += 1
            ddi = append_DdiFact(drug, query_task)  # Если есть то сохраняем предложение в локальную бд
            for i in drug['drugs']:  # Циклом сохраняем все ссылки на препараты в этом предложении в локальную бд
                append_Drug(i, ddi)

    print(f'Из {len(drug_dict)} обработанных Bert добавили в бд {j}')  # Выводим в консоль кол-во обработанных и загруженных в бд предложений
    try:  # смотрим есть ли скачанные предложения по этому PMID в бд, если есть то выводим о них информацию на страницу
        drug = drug_dict[-1]
        ddi_id = drug['id_doc']
    except:  # Если нет то присваиваем им None
        ddi_id = None
    return ddi_id


# создаем ddi данные в бд
def append_DdiFact(drug, task):
    ddi = DdiFact(
        id_task=task,
        id_doc=drug['id_doc'],
        sentence_txt=drug['sentence_txt'],
        parsing_txt=drug['parsing_txt'],
        numb_sentence_in_doc=drug['numb_sentence_in_doc'],
        ddi_type=drug['ddi_type']
    )
    ddi.save()
    return ddi


# создаем ссылки на препараты от ddi
def append_Drug(drug, ddi):
    drug = DrugLink(
        id_fact=ddi,
        drug_name=drug
    )
    drug.save()


# Заходим в PubMed и получаем документы
def get_access_to_PubMed(email, search_str, source):
    Entrez.email = email  # Майл пользователя
    handle = Entrez.esearch(db=source, sort='relevance', term=search_str, retmax='10000')
    record = Entrez.read(handle)
    rec_count = record['Count']  # Кол-во найденных записей
    print(search_str, ' - ', rec_count)

    idlist = record["IdList"]
    handle = Entrez.efetch(db=source, id=idlist, rettype="medline", retmode="text")
    records = Medline.parse(handle)  # Записываем все данные
    return rec_count, records


# Готовим список документов в Bert
def docs_to_db(records):
    num = 0
    docs = []
    for record in records:  # Проходим циклом по каждой записи
        if check_in_database(record) == False:    #проверяем запись на наличие в локальной бд, если есть то пропускаем
            pass
        else:  # Если нет то сохраняем
            num += 1
            doc = save_in_doc(record)  # Ф-я сохранения
            docs.append(doc)
        if num == 50:# --> Временное ограничение, потом убрать!
            print(record.keys())
            break
    return docs


# проверяем запись на наличие в нашей бд если нет то сохраняем
def check_in_database(record):
    try:
        id = record['PMID']
    except:
        id = record['PMC']  # Проверям на наличие документа в бд
        id = id[3:]
    if DdiFact.objects.filter(id_doc=id).exists():  # Если есть такой PMID в нашей бд то пропускаем
        return False
    else:
        return True


# готовим файл в bert
def save_in_doc(record):  # --> Добавить страну и авторов для вывода!!!
    doc = []
    try:
        doc.append(record['PMID'])  # Сохраняем PMID записи для дальнейшего вывода ссылки на оригинал и проверки на наличие в бд
    except:
        id = record['PMC']
        id = id[:3]
        doc.append(id)  # Если нет PMID то сохраняем его PMC
    try:
        title = str(record['TI'])  # Сохраняем заголовок
    except:
        title = ' . '
    try:
        abstract = str(record['AB'])
        abstract = title + abstract  # Сохранием содержание
    except:
        abstract = ' . '
    try:
        main_author = str(record['AU'][0])
    except:
        main_author = 'Nobody'
    try:
        main_place = str(record['AD'][0])
    except:
        main_place = 'Anywhere'
    doc.append(title)
    doc.append(abstract)
    doc.append(main_author)
    doc.append(main_place)
    return doc


# Создаем пользовательский запрос
def create_task(source, query_text, query_begin, query_end, username):
    source = Source.objects.get(name=source)  # получаем сайт откуда брали данные
    user = User.objects.get(username=username)  # пользователя который сделал запрос
    query_task = Task(source_id=source, query_text=query_text,
                      date_start=query_begin, date_end=query_end, username=user)  # получаем запрос
    query_task.save()

    task_id = query_task.id_task  # созраняем в запросе id задания которое выполняет воркер
    return task_id



