FROM python:3.6
ENV FLASK_APP=screeps_loan/screeps_loan.py
ENV SETTINGS=/app/settings
ENV FLASK_RUN_CERT=adhoc

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "3", "-b", ":5000", "screeps_loan.screeps_loan:app"]
