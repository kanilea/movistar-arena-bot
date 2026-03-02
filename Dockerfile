FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
│      && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
│      && apt-get update \
│      && apt-get install -y google-chrome-stable \
│      && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
COPY movistar_arena_bot.py .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Descargar ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    chmod +x chromedriver && \
    mv chromedriver /usr/local/bin/

# Configurar sandbox para Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/local/bin/chromedriver

# Exponer puerto (si necesitas web interface)
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "movistar_arena_bot.py"]
