FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENV=prod

WORKDIR /app

# Instalar uv
RUN pip install --no-cache-dir uv

# Instalar dependencias del proyecto (solo producción)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# Copiar código fuente
COPY . .

# Crear directorio para la base de datos
RUN mkdir -p /app/data /app/media /app/staticfiles

# Recopilar estáticos (sin SECRET_KEY real — se usa un placeholder)
RUN DJANGO_SECRET_KEY=build-placeholder .venv/bin/python manage.py collectstatic --noinput

EXPOSE 8000

RUN chmod +x scripts/entrypoint.sh

ENTRYPOINT ["scripts/entrypoint.sh"]
