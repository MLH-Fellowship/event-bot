FROM python:3.7-buster
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
ENTRYPOINT [ "python3", "app/bot.py" ]