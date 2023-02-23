FROM python:3.8-slim
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y python3-pip
RUN mkdir /home/api
WORKDIR /home/api
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 3000
CMD [ "flask", "run", "-p", "3000", "--host", "0.0.0.0"]
