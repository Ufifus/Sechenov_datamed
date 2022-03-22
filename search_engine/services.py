from django.contrib.auth.models import User

from .models import DdiFact, Task, Source, DrugLink
from .tasks import get_PubMed_data_list as task_PubMed
from .logics import get_access_to_PubMed as get_docs
from .logics import docs_to_db, create_task

from django_celery_results.models import TaskResult
from celery.result import AsyncResult

import sys

from pathlib import Path

path_to_bert = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'BERT_core'))
sys.path.append(path_to_bert)



# Получаем данные из локальной бд
def get_articles_from_db(query):
    if query == 'all':
        db_objs = DdiFact.objects.all()
    else:
        db_objs = DdiFact.objects.filter(sentence_txt__icontains=query)
    return list(db_objs.values())


# запускаем celery-worker
def run_query(email, search_string, query_task_id, source):
    count, records = get_docs(email, search_string, source)  # Получаем записи и их количество из запроса в PubMed
    print(count)
    print(source)
    if int(count) == 0:  # Если нет таких то выводим на сайт
        task_id = None
        print('this done')
    else:
        docs = docs_to_db(records)  # Если есть то проверяем их на валидность и новый массив документов загружаем в Bert

        task = task_PubMed.delay(docs, query_task_id)  # Запускаем worker-accync
        task_id = task.id  # Получаем id нашего воркера для отслеживания статуса

        task_query = Task.objects.get(id_task=query_task_id)  #Находим наш запрос и сохраняем в нем id задания
        task_query.task_back = str(task_id)
        task_query.save()

    return task_id, count


"""
    Отслеживаем выполнение запросов
        1. Если выполняется то выводим статус задания
        2. Если выполнен то не выводим его 

"""
def get_query_status(username):
    user = User.objects.get(username=username)
    tasks_query = Task.objects.filter(username=user).order_by('-query_time')[0]
    print(tasks_query)
    task_id = tasks_query.task_back
    if task_id:
        task_worker = TaskResult.objects.get(task_id=task_id)
        if task_worker.status != 'PROGRESS':
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

