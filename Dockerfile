FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1 APP_HOME=/micro/

RUN mkdir $APP_HOME && adduser --system --home /home/python python \
    && chown -R python $APP_HOME

WORKDIR $APP_HOME

ADD requirement*.txt $APP_HOME
ADD . $APP_HOME
RUN apt-get update \
    && pip install -r requirements.txt


USER python
# CMD ["python3.7", "manage.py", "runserver"]