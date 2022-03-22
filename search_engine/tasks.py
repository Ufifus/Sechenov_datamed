from celery import shared_task
from celery_progress.backend import ProgressRecorder, AbstractProgressRecorder
import sys
from decimal import Decimal

from pathlib import Path

path_to_bert = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'BERT_core'))
sys.path.append(path_to_bert)

from .logics import *


"""Получаем набор данных, запускаем воркер ассинхронно от сайта, и в цикле пробегаем по каждой сохраненной записи
выводя информацию на экран, в кол-ве обработанных записей и информацию о данной:
    1. PMID
    2. Страну публикации
    3. Авторов
    4. Заголовок"""
@shared_task(bind=True)
def get_PubMed_data_list(self, docs, query_task_id):
    progress_recoder = UpdateProgressrecorder(self)  # Наследуем task_result для сохраниния статуса и вывода информации
    num_all_docs = len(docs)  # Узнаем кол-во сохраненных документов

    query_task = Task.objects.get(id_task=query_task_id)  # Находим наш запрос в бд и сохраняем в нем id задания worker
    query_text = f'{query_task.query_text} {query_task.date_start} до {query_task.date_end}'  # Выводим информацию о запросе на страницу

    data_mas = []  # Массив данных куда мы вносим обработанную запись для вывода

    for num, doc in enumerate(docs):  # Запускаем цикл который проходит по записям и анализирует их
        try:
            ddi_id = analise_doc(doc[:3], query_task)  # Загрузаем запись в Bert
        except:
            # Делаем проверку т.к выскакивает проблема с кешем у трансформеров
            ddi_id = 'Fail'
        if ddi_id is None:  # Если по данному PMID нет сохраненных записей выводим информацию!!!

            str = 'В документе не пайденно взаимодействий'
            data = None
        else:
            if ddi_id == 'Fail':  # Если происходит ошибка то пишем это на страницу, потом спросить в чем проблема у преподавателя!!!
                str = f'Что-то пошло не так'
            else:
                str = f''
            try:
                title_pres = doc[1][:50]
            except:
                title_pres = doc[1]
            data = {
                'PMID': doc[0],
                'title': title_pres,
                'author': doc[3],
                'place': doc[4]
            } # Получаем данные если есть и выводим в виде таблицы

        progress_recoder.set_progress(num + 1, num_all_docs, query_text + ';' + str, data)


PROGRESS_STATE = 'PROGRESS'


# Ф-я для отслеживания статуса измененная из celery_progress с добавлением данных
class UpdateProgressrecorder(AbstractProgressRecorder):
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



