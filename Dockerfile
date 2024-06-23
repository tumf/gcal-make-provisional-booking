FROM python:3.11-slim
WORKDIR /app
COPY envvars.py /app/envvars.py
COPY google_api_util.py /app/google_api_util.py
COPY keep_available_slots.py /app/keep_available_slots.py
COPY remove_all_keeps.py /app/remove_all_keeps.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "keep_available_slots.py" ]