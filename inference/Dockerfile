# Minimal, production-ready image for transformer CPU inference.

# 1. Buena práctica (pinnear versiones): fijamos la versión exacta a nivel de parche (3.12.7)
# para builds reproducibles, evitando que tags flotantes (como 3.12-slim) rompan el entorno al actualizarse.
FROM python:3.12.7-slim

WORKDIR /app

# 2. Buena práctica (Python y ML en contenedores):
# - PYTHONUNBUFFERED=1 asegura que los logs salgan directo a stdout/stderr en tiempo real.
# - PYTHONDONTWRITEBYTECODE=1 evita generar archivos .pyc en las capas.
# - HF_HOME especifica el directorio de caché para los pesos de Hugging Face.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/home/appuser/.cache/huggingface \
    PORT=8081

# 3. Buena práctica (seguridad / menor privilegio): no correr como root (UID 0).
# Creamos el usuario 'appuser' (UID 1000) y su directorio de caché con permisos adecuados.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /home/appuser/.cache/huggingface \
    && chown -R appuser:appuser /home/appuser

# 4. Buena práctica (orden por frecuencia de cambio): primero dependencias para aprovechar la caché de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Buena práctica (evitar capas redundantes): asignamos propiedad a 'appuser' directamente en el COPY.
COPY --chown=appuser:appuser serve.py .

USER appuser

EXPOSE 8081

# 6. Healthcheck nativo consultando el endpoint /healthz implementado en serve.py.
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://localhost:%s/healthz' % os.environ.get('PORT', '8081'), timeout=2)"]

CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8081"]