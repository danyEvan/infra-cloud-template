# Minimal, student-readable image for the servicio patron.

# 1. Buena práctica (pinnear versiones): fijamos la versión exacta a nivel de parche (3.12.7)
# para garantizar builds reproducibles, evitando que tags flotantes (como 3.12-slim) rompan el entorno al actualizarse.
FROM python:3.12.7-slim

WORKDIR /app

# 2. Buena práctica (Python en contenedores):
# PYTHONUNBUFFERED=1 asegura que los logs salgan directo a stdout/stderr en tiempo real sin quedar en buffer (clave para docker logs y Kubernetes).
ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    PORT=8080

# 3. Buena práctica (seguridad / menor privilegio): no correr como root (UID 0).
# Creamos el usuario 'appuser' (UID 1000) y preparamos /data con los permisos correctos.
# /data no tiene instrucción VOLUME a propósito: evita volúmenes anónimos huérfanos sin -v.
# NOTA: si montás un directorio del host que pertenece a root, ejecutá
# 'sudo chown -R 1000:1000 <directorio>' en el host antes de correr el contenedor para evitar PermissionError (HTTP 500).
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data

# 4. Buena práctica (orden por frecuencia de cambio): primero dependencias para aprovechar la caché de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Buena práctica (evitar capas redundantes): usamos --chown directamente en el COPY.
# Esto asigna la propiedad a 'appuser' al momento de copiar, evitando un 'RUN chown -R' posterior
# que duplicaría el archivo en una capa adicional de la imagen.
COPY --chown=appuser:appuser main.py .

USER appuser

EXPOSE 8080

# `docker ps` shows (healthy) once /healthz answers. Kubernetes ignores this
# and uses the chart's probes instead.
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=10 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://localhost:%s/healthz' % os.environ.get('PORT', '8080'), timeout=2)"]

CMD ["python", "main.py"]
