FROM python:3.8
ENV FLASK_APP=screeps_loan/screeps_loan.py
ENV FLASK_RUN_CERT=adhoc

# Make sure we have up-to-date SSL certs
RUN pip install --upgrade pip certifi

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "3", "-b", ":5000", "screeps_loan.screeps_loan:app"]
