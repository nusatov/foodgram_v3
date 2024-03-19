FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY ./entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV SECRET_KEY=${SECRET_KEY}

EXPOSE 8000

CMD ["entrypoint.sh"]

