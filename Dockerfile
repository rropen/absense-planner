FROM python:3.8

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . rr_absence
WORKDIR /rr_absence

EXPOSE 8000

ENTRYPOINT [ "python", "ap_src/manage.py" ]
CMD [ "runserver", "0.0.0.0:8000" ]