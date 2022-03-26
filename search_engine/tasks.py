from celery import shared_task
from celery_progress.backend import AbstractProgressRecorder
from decimal import Decimal

from .logics import *


"""Получаем набор данных, запускаем воркер ассинхронно от сайта, и в цикле пробегаем по каждой сохраненной записи
   выводя информацию на экран, в кол-ве обработанных записей и информацию о данной:
    1. PMID
    2. Страну публикации
    3. Авторов
    4. Заголовок"""
@shared_task(bind=True)
def get_PubMed_data_list(self, records, query_task_id):
    progress_recoder = UpdateProgressrecorder(self)  # Наследуем task_result для сохраниния статуса и вывода информации
    num_all_docs = len(records)  # Узнаем кол-во сохраненных документов

    query_task = Task.objects.get(id_task=query_task_id)  # Находим наш запрос в бд и сохраняем в нем id задания worker
    query_text = f'{query_task.query_text} {query_task.date_start} до {query_task.date_end}'  # Выводим информацию о запросе на страницу

    data_mas = []  # Массив данных куда мы вносим обработанную запись для вывода

    for num, record in enumerate(records):  # Запускаем цикл который проходит по записям и анализирует их
        clear_doc = Analise_record(_record=record, _query_task=query_task)
        result_str, data = clear_doc.ahalise_doc()
        progress_recoder.set_progress(num + 1, num_all_docs, query_text + '; ' + result_str, data)


@shared_task(bind=True)
def parse_and_analise_docs(self, handle, count, query_task_id):
    """Задача которая принимает группу подзадач с каждым документом обработки """


PROGRESS_STATE = 'PROGRESS'

class UpdateProgressrecorder(AbstractProgressRecorder):
    """Класс для отслеживания статуса измененная из celery_progress с добавлением данных"""
    def __init__(self, task):
        self.task = task

    def set_progress(self, current, total, description="", data=None):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        state = PROGRESS_STATE
        meta = {
            'pending': False,
            'current': current,
            'total': total,
            'percent': percent,
            'description': description,
            'data': data
        }
        self.task.update_state(
            state=state,
            meta=meta
        )
        return state, meta
