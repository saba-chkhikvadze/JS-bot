FROM python:3.9
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get install -y ffmpeg
COPY . /bot/
CMD python bot.py