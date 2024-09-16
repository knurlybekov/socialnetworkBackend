## pull official base image
#FROM python:3.11.4-slim-buster
#
## set work directory
#WORKDIR /usr/src/app
#
## set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## install dependencies
#RUN pip install --upgrade pip
#COPY ./requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
## Install Nginx
#RUN apt-get update && apt-get install -y nginx
#
## Copy your self-signed certificate and private key
#COPY ./cert.pem /etc/ssl/certs/cert.pem
#COPY ./privkey.pem /etc/ssl/certs/privkey.pem
#
## Copy your Nginx configuration file
#COPY ./nginx.conf /etc/nginx/conf.d/default.conf
#
## Expose the port Nginx will run on
#EXPOSE 443 80
## copy project
#COPY . .
#
##CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
#
## Run Gunicorn to serve your Django application
##CMD ["gunicorn", "--bind", "0.0.0.0:8000", "acadebeatmain.wsgi:application"]
#CMD sh -c "python manage.py makemigrations && python manage.py migrate && gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 acadebeat.wsgi:application"

#FROM python:3.11.4-slim-buster
#
## set work directory
#WORKDIR /usr/src/app
#
## set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## Install system dependencies
#RUN apt-get update \
#    && apt-get install -y gcc libffi-dev musl-dev build-essential \
#    && apt-get clean
#
## install dependencies
#RUN pip install --upgrade pip
#COPY ./requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
## copy project
#COPY . .
#EXPOSE 8000
#
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# run python command
#RUN python manage.py makemigrations
#RUN python manage.py migrate

# Expose the port for the application (Gunicorn will run on 8000)
#CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
# Default command to run the app with Gunicorn
#CMD ["gunicorn", "acadebeat.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc libffi-dev musl-dev build-essential \
    && apt-get clean

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# expose port 8000
EXPOSE 8000

# run gunicorn server
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "acadebeat.wsgi:application"]
