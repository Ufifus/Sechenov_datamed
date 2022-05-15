FROM python:3.9

WORKDIR /usr/src/datamed

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/datamed/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/datamed/

COPY ./entrypoint.sh /usr/src/datamed/entrypoint.sh

EXPOSE 8000

#CMD ['python', 'manage.py', 'makemigrations']
CMD ['python', 'manage.py', 'migrate']
#ENTRYPOINT ["/usr/src/datamed/entrypoint.sh"]