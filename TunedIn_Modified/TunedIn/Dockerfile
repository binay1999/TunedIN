FROM python:3.8-alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 9200
CMD ["python3", "app.py"]