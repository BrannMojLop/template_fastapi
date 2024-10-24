FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN apt update && apt install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

COPY . .

RUN mv .aws ~/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]