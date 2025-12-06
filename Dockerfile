FROM python:3.11-slim

# Crear usuario non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Establecer directorio de trabajo
WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY app/ ./app/
COPY scripts/ ./scripts/
COPY evidence/ ./evidence/

# Cambiar permisos al usuario appuser
RUN chown -R appuser:appuser /app


USER appuser


EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
