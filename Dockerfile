FROM python:3.11.8-slim-buster

WORKDIR /app

COPY Requirement.txt Requirement.txt

RUN pip install -r Requirement.txt

COPY . .

EXPOSE 8000

CMD python manage.oy runserver