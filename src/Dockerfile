FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python util.py && python config.py && python provenance_holder.py
