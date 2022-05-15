from django.contrib.auth.models import User

from .models import DdiFact, Task, Source
from .tasks import get_PubMed_data_list as task_PubMed
from .logics import get_global_data
from .models import DdiDocument

from django_celery_results.models import TaskResult

import sys
from pathlib import Path

path_to_bert = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'BERT_core'))
sys.path.append(path_to_bert)


def get_articles_from_db(query):
    """Получаем данные из локальной бд"""
    if query == 'all':
        db_objs = DdiFact.objects.all().values()
    else:
        db_objs = DdiFact.objects.filter(sentence_txt__icontains=query).values()
    for i, obj in enumerate(db_objs):
        db_objs[i]['id_doc_id'] = DdiDocument.objects.get(id_doc=obj['id_doc_id']).id_record
    return list(db_objs)


def get_docs(db_tasks):
    db_full_docs = []
    for db_task in db_tasks:
        db_docs_q = DdiDocument.objects.filter(task_query=db_task)
        db_docs = list(db_docs_q.values())
        for i, db_doc_q in enumerate(db_docs_q):
            db_docs[i]['authors'] = list(db_doc_q.authors.all().values())
            db_docs[i]['places'] = list(db_doc_q.places.all().values())
            db_docs[i]['ddi_facts'] = list(DdiFact.objects.filter(id_doc=db_doc_q).values())
            db_full_docs.append(db_docs[i])
    print(db_full_docs[1].keys())
    return db_full_docs


def run_query_v1(email, search_string, query_task_id, source):
    """1. Выполняем запрос в глобальные бд
    2. Затем полученные данные выгружаем в воркер и обновляем task
    в бд привязывая к ней номер таска который выполняет запрос"""
    idlist, count = get_global_data(email, source, search_string)
    if int(count) == 0:  # Если нет таких то выводим на сайт
        task_id = None
        print('this clear')
    else:
        task = task_PubMed.delay(idlist, query_task_id, source)  # Запускаем worker-accync
        task_id = task.id  # Получаем id нашего воркера для отслеживания статуса
        task_query = Task.objects.get(id_task=query_task_id)  # Находим наш запрос и сохраняем в нем id задания
        task_query.task_back = str(task_id)
        task_query.save()
    return task_id, count


def get_query_status(username):
    """ Отслеживаем выполнение запросов
        1. Если выполняется то выводим статус задания
        2. Если выполнен то не выводим его """
    user = User.objects.get(username=username)
    if Task.objects.filter(username=user).exists():
        tasks_query = Task.objects.filter(username=user).order_by('-query_time')[0]
        print(tasks_query)
        task_id = tasks_query.task_back
        if task_id:
            try:
                task_worker = TaskResult.objects.get(task_id=task_id)
                if task_worker.status != 'PROGRESS':
                    task_id = None
            except:
                task_id = None
    else:
        task_id = None
    return task_id


# Получаем на основе формы запрос в бд пабмеда
def get_search_string(dict):
    for key, value in dict.items():
        if key == 'query_begin':
            date_begin = create_data(value)
        elif key == 'query_end':
            date_end = create_data(value)
        elif key == 'user_query':
            text = value
        elif key == 'query_source':
            print(value)
            source = value.name
    string = f'{text} and {date_begin}:{date_end}[dp]'
    return string, source


# создаем сроку с датой
def create_data(data):
    date = str(data).split('-')
    date = '/'.join(date)
    return date


# Создаем пользовательский запрос
def create_task(source, query_text, query_begin, query_end, username):
    source = Source.objects.get(name=source)  # получаем сайт откуда брали данные
    user = User.objects.get(username=username)  # пользователя который сделал запрос
    query_task = Task(source_id=source, query_text=query_text,
                      date_start=query_begin, date_end=query_end, username=user)  # получаем запрос
    query_task.save()

    task_id = query_task.id_task  # созраняем в запросе id задания которое выполняет воркер
    return task_id