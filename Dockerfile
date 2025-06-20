FROM python:3.11.9

COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir -r pyproject.toml

COPY . rr_absence
WORKDIR /rr_absence

EXPOSE 8000

ENTRYPOINT [ "python", "ap_src/manage.py" ]
CMD [ "runserver", "0.0.0.0:8000" ]