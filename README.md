Сайт по поиску лекарственных взаимодейстий между препаратами

для работы нужно:

    1. Mysql бд
    2. Redis бд

Подключение к редису идет в файле .env, там же настроики кондефенциальности сайта

команды выполнять в директории с manage.py:

    для django

        1. python manage.py migrate

        2. python manage.py runserver


    для celery 
        
        Если windows

            1. celery -A datamed worker -l info -P eventlet
    
        Если linux
        
            1. celery -A datamed worker -l info

    для flower
        
        2. celery -A datamed flower


    


    
