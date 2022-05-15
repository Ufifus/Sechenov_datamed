from celery import shared_task
from celery_progress.backend import AbstractProgressRecorder
from decimal import Decimal
import time

from datamed import settings
from .models import Task
from .logics import *

# Get Parser_core for parsing data
path_to_parser = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'Parser_core'))
sys.path.append(path_to_parser)

from Parser_core.Scraber import Scraber, Driver
from Parser_core.Parsers import return_parser


"""Получаем набор данных, запускаем воркер ассинхронно от сайта, и в цикле пробегаем по каждой сохраненной записи
   выводя информацию на экран, в кол-ве обработанных записей и информацию о данной:
    1. PMID
    2. Страну публикации
    3. Авторов
    4. Заголовок"""
@shared_task(bind=True)
def get_PubMed_data_list(self, idlist, query_task_id, source):
    progress_recoder = UpdateProgressrecorder(self)  # Наследуем task_result для сохраниния статуса и вывода информации
    num_all_docs = len(idlist)  # Узнаем кол-во сохраненных документов

    query_task = Task.objects.get(id_task=query_task_id)  # Находим наш запрос в бд и сохраняем в нем id задания worker
    query_text = f'{query_task.query_text} {query_task.date_start} до {query_task.date_end}'  # Выводим информацию о запросе на страницу

    scraber = Scraber.create_scraber(config_parser, source)
    parser = return_parser(source)

    for num, page_id in enumerate(idlist):  # Запускаем цикл который проходит по записям и анализирует их
        start_time = time.time()
        page, page_id = scraber.get_page(page_id)
        if page:
            record = parser.parce(page, page_id)
            for k, v in record.items():
                print(k, '-->', v)
            clear_doc = Analise_record(_record=record, _query_task=query_task)
            result_str, data = clear_doc.ahalise_doc()
        else:
            data = None
            result_str = 'не удалось получить доступ к странице'
        end_time = time.time()  # Проверяем время выполнения чтобы сайт не заподозрил бота
        progress_time = int(end_time - start_time)
        if progress_time < 10:
            time.sleep(10 - progress_time)
        progress_recoder.set_progress(num + 1, num_all_docs, query_text + '; ' + result_str, data)


config_parser = {
    'User-Agent': settings.PARCER_USER_AGENT,
    'Accept': settings.RARCER_ACCEPT,
}


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
