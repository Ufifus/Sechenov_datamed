Сайт по поиску лекарственных взаимодейстий между препаратами

для работы нужно:

    1. Mysql бд
    2. Redis бд

Подключение к редису идет в файле .env, там же настроики кондефенциальности сайта

команды выполнять в директории с manage.py:

    для django

        1. python manage.py makemigrations

        2. python manage.py migrate

        3. python manage.py runserver


    для celery

        1. celery -A datamed worker -l info -P eventlet
    

    для flower
        
        2. celery -A datamed flower


    


    
