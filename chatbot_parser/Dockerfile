FROM python:3.9.5

COPY . /chatbotParser

WORKDIR /chatbotParser

RUN pip install -r requirements.txt
RUN pip install requests

CMD python ./chatbotParser.py