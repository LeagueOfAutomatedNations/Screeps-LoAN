FROM python:3.5
ENV FLASK_APP=screeps_loan/screeps_loan.py
ENV SETTINGS=/app/settings
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
CMD ["gunicorn","-w","3","-b",":5000","screeps_loan.screeps_loan:app"]