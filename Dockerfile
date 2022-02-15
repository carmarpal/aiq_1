FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1 APP_HOME=/micro/

RUN mkdir $APP_HOME && adduser --system --home /home/python python \
    && chown -R python $APP_HOME

WORKDIR $APP_HOME

ADD requirement*.txt $APP_HOME
ADD . $APP_HOME
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libev-dev python3.7-dev git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc python3.7-dev git


EXPOSE 5000
USER python
CMD python3.7 ${APP_HOME}manage.py runserver