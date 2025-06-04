FROM python:3.11.8-slim

# Define o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean

# Copia o requirements.txt para o contêiner
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o contêiner
COPY . /app

# Porta para expor
EXPOSE 10000