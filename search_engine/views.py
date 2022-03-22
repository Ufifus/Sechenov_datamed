from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.views.generic import FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from celery_progress.views import get_progress
from datamed.celery import app
from django_celery_results.models import TaskResult

from .services import *
from .logics import create_task
from .forms import AddSearchForm, AddLocalSearch

import json
import sys
from pathlib import Path
from datetime import date

path_to_bert = str(Path.joinpath(Path(__file__).resolve().parent.parent, 'BERT_core'))
sys.path.append(path_to_bert)


# поиск в pubmed
class SearchPubmedView(LoginRequiredMixin, View):
    template_name = 'search_engine/search_pubmed.html'
    search_form = AddSearchForm

    def get(self, request, *args, **kwargs):
        username = request.user.username  # Получаем пользователя который выполнил запрос
        list_tasks = get_query_status(username)  # Получаем статус выполнения его задачи

        context = {
            'form': self.search_form,  # выводим форму для запроса
            'task_id': list_tasks,  # выводим статус задания
        }
        return render(request, self.template_name, context)

    """Получая форму мы проверяем ее на валидность и если все хорошо, то пускаем ее на обработку в Bert"""
    def post(self, request, *args, **kwargs):
        form = self.search_form(request.POST)
        if form.is_valid():
            print('good')
            username = request.user.username

            print(form.cleaned_data)
            vals = form.cleaned_data
            query, source = get_search_string(vals)

            # Создаем запрос
            query_task_id = create_task(source, vals['user_query'], vals['query_begin'], vals['query_end'], username)

            if source == 'PubMed' or 'PMC':
                email = "tens223155@gmail.com"  # Указываем почту пользователя для запроса, пока моя заменить!!!
                print(query)

                task_id, count = run_query(email, query, query_task_id, source)  # Возварщаем кол-во записей и статус задачи
            else:
                return HttpResponse('<p>Пока не добавлена такая функция</p>')  # Для других ресурсов потом добавить!!!

            return render(request, self.template_name,
                                   context={'form': self.search_form, 'count': count, 'task_id': task_id})
        return render(request, self.template_name, {'form': self.search_form})


# поиск в локальной бд
class SearchLocalView(LoginRequiredMixin, FormView):
    template_name = 'search_engine/search_local.html'
    search_form = AddLocalSearch

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск в локальной базе данных'
        return context

    def get(self, request, *args, **kwargs):
        form = self.search_form(request.GET)
        if form.is_valid():
            query = form['user_query'].value()
            data_list = get_articles_from_db(query)
            count = len(data_list)
            return render(request, self.template_name,
                          {'form': form,
                           'count': count,
                           'db_data_list': json.dumps(data_list)})
        return render(request, self.template_name, {'form': self.search_form})


# Останавливаем выполнение анализа документов и  Перенаправляем на главную
class StopTask(LoginRequiredMixin, View):

    def get(self, request, task_id):
        if request.method == 'GET':
            app.control.revoke(task_id, terminate=True)  # Останавливаем задачу обработка workera
            task = TaskResult.objects.get_task(task_id=task_id)   # Присваиваем задачи статус выполнен в запросе
            task.status = 'SUCCESS'
            task.save()
            return redirect('/')
