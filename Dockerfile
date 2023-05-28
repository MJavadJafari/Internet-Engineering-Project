FROM python:3.10
# ENV test=1
WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000

CMD ["python" , "manage.py", "runserver", "0.0.0.0:8000"]
 