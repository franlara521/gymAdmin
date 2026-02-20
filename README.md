# GymAdmin

Aplicación web de administración para un gimnasio de entrenamiento funcional.
Tres portales independientes: Superadmin, Entrenador y Cliente.
Desarrollada en Django con despliegue en Kubernetes.

---

## Inicio rápido — datos de demo incluidos

```bash
# 1. Instalar dependencias
uv sync

# 2. Aplicar migraciones
.venv/bin/python manage.py migrate

# 3. Cargar datos de demostración (entrenadores, clientes, clases, planes, mensajes)
.venv/bin/python manage.py create_demo_data

# 4. Arrancar el servidor
.venv/bin/python manage.py runserver
```

Abrir http://localhost:8000 — redirige automáticamente al portal según el rol del usuario.

### Usuarios de demo

| Usuario | Contraseña | Rol | Portal |
|---------|-----------|-----|--------|
| `admin` | `admin1234` | Superadmin | http://localhost:8000/portal/admin/ |
| `ana.garcia` | `trainer1234` | Entrenadora (CrossFit) | http://localhost:8000/portal/trainer/ |
| `marcos.herrero` | `trainer1234` | Entrenador (HIIT+Fuerza) | http://localhost:8000/portal/trainer/ |
| `laura.sanchez` | `trainer1234` | Entrenadora (Yoga) | http://localhost:8000/portal/trainer/ |
| `carlos.ruiz` | `client1234` | Cliente | http://localhost:8000/portal/client/ |
| `elena.martin` | `client1234` | Cliente | http://localhost:8000/portal/client/ |
| *(+6 clientes)* | `client1234` | Cliente | http://localhost:8000/portal/client/ |

---

## Portales

| Portal | URL | Acceso | Nav |
|--------|-----|--------|-----|
| Login | `/auth/login/` | Todos | — |
| **Cliente** | `/portal/client/` | `is_staff=False` | Azul |
| **Entrenador** | `/portal/trainer/` | `is_staff=True, is_superuser=False` | Ámbar |
| **Superadmin** | `/portal/admin/` | `is_superuser=True` | Oscuro |
| Django admin | `/django-admin/` | Superusuario | — |

La redirección post-login es automática: el sistema lleva a cada usuario a su portal.

### ¿Qué puede hacer cada rol?

**Superadmin** — control total del gimnasio:
- Alta y edición de clientes y entrenadores
- Creación de tipos de clase y clases programadas
- Asignación de planes de entrenamiento
- Vista de todas las conversaciones
- Dashboard global con KPIs y gráficos

**Entrenador** — gestión de su propia actividad:
- Horario semanal filtrado a sus clases
- Marcado de asistencia clase por clase
- Creación y edición de planes para sus clientes
- Inbox con mensajes de sus clientes
- Dashboard propio (tasa de asistencia, clientes únicos, gráfico de reservas)

**Cliente** — experiencia del miembro:
- Horario semanal con reserva/cancelación de plazas (sin recarga de página)
- Vista de planes de entrenamiento asignados
- Mensajería con el gimnasio
- Dashboard personal con historial y próximas reservas

---

## Desarrollo local

### Opción A — con `uv` (recomendado)

```bash
# Instalar uv si no lo tienes
pip install uv

# Crear entorno virtual e instalar dependencias de desarrollo
uv sync

# Aplicar migraciones y cargar datos de demo
.venv/bin/python manage.py migrate
.venv/bin/python manage.py create_demo_data

# Arrancar el servidor
.venv/bin/python manage.py runserver
```

### Opción B — con pip estándar

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python manage.py migrate
python manage.py create_demo_data
python manage.py runserver
```

### Crear usuarios manualmente

```bash
# Superadmin (llega al portal /portal/admin/)
.venv/bin/python manage.py createsuperuser

# Entrenador (llega al portal /portal/trainer/)
# → Crear desde el portal superadmin: /portal/admin/trainers/create/

# Cliente (llega al portal /portal/client/)
# → Crear desde el portal superadmin: /portal/admin/clients/create/
```

### Resetear la base de datos

```bash
# Limpia y regenera todos los datos de demo
.venv/bin/python manage.py create_demo_data --reset

# O reset completo desde cero
rm data/db.sqlite3
.venv/bin/python manage.py migrate
.venv/bin/python manage.py create_demo_data
```

---

## Base de datos (SQLite)

SQLite almacena toda la información en un único fichero. Su comportamiento varía según el entorno.

### Local

El fichero se crea en `data/db.sqlite3` al ejecutar `migrate`. Excluido del repositorio.

```bash
# Backup manual
cp data/db.sqlite3 data/db_backup_$(date +%Y%m%d).sqlite3

# Aplicar migraciones tras cambiar un modelo
.venv/bin/python manage.py makemigrations <app>
.venv/bin/python manage.py migrate
```

### Docker

En el contenedor, la DB vive en `/app/data/db.sqlite3`. Requiere volumen para persistir.

```bash
# Con persistencia
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="dev-secret-key" \
  -e DJANGO_ENV=dev \
  -v "$(pwd)/data:/app/data" \
  gymadmin:dev

# Cargar datos de demo dentro del contenedor
docker exec -it <container_id> /bin/sh
.venv/bin/python manage.py create_demo_data
```

### Kubernetes

La DB se almacena en un PersistentVolumeClaim (`gymadmin-db-pvc`).
Las migraciones se aplican automáticamente en cada deploy vía `entrypoint.sh`.
Un CronJob hace backup automático cada día a las 3 AM (retiene 30 copias).

```bash
# Cargar datos de demo
kubectl exec -n gymadmin-dev -it deployment/gymadmin -- /bin/sh
.venv/bin/python manage.py create_demo_data

# Backup manual inmediato
kubectl create job --from=cronjob/gymadmin-db-backup backup-manual-$(date +%Y%m%d) -n gymadmin-dev

# Restaurar backup
kubectl exec -n gymadmin-dev -it deployment/gymadmin -- /bin/sh
cp /app/backups/db_FECHA.sqlite3 /app/data/db.sqlite3
exit
kubectl rollout restart deployment/gymadmin -n gymadmin-dev
```

> **Regla crítica:** `replicas: 1` y `strategy: Recreate` son obligatorios con SQLite.
> Múltiples réplicas corrompen la base de datos. Migrar a PostgreSQL antes de escalar.

---

## Docker — construcción y ejecución

```bash
# Construir imagen
docker build -t gymadmin:dev .

# Ejecutar con datos persistentes
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="una-clave-secreta-larga" \
  -e DJANGO_ENV=dev \
  -e DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1" \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/media:/app/media" \
  gymadmin:dev
```

El contenedor ejecuta automáticamente `migrate` y arranca `gunicorn` en el puerto 8000.

### Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DJANGO_SECRET_KEY` | **Sí** | Clave secreta Django (mín. 50 caracteres) |
| `DJANGO_ENV` | No | `dev` o `prod` (default: `prod`) |
| `DJANGO_ALLOWED_HOSTS` | En prod | Hosts separados por coma |
| `DB_PATH` | No | Ruta al SQLite (default: `/app/data/db.sqlite3`) |
| `MEDIA_ROOT` | No | Directorio de uploads (default: `/app/media`) |

```bash
# Generar SECRET_KEY segura
python -c 'import secrets; print(secrets.token_urlsafe(50))'
```

---

## Despliegue en Kubernetes

### Primer despliegue

```bash
# 1. Construir imagen
docker build -t gymadmin:dev .

# 2. Crear namespace y Secret
kubectl create namespace gymadmin-dev
kubectl create secret generic gymadmin-secret \
  --namespace gymadmin-dev \
  --from-literal=DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"

# 3. Aplicar manifiestos
kubectl apply -k k8s/overlays/dev/

# 4. Verificar que el pod está Running
kubectl get pods -n gymadmin-dev -w

# 5. Cargar datos de demo
kubectl exec -n gymadmin-dev -it deployment/gymadmin -- \
  .venv/bin/python manage.py create_demo_data
```

### Actualizar tras cambios de código

```bash
docker build -t gymadmin:dev .
kubectl rollout restart deployment/gymadmin -n gymadmin-dev
kubectl rollout status deployment/gymadmin -n gymadmin-dev
```

### Producción

```bash
# Actualizar imagen en k8s/overlays/prod/kustomization.yaml, luego:
kubectl apply -k k8s/overlays/prod/
```

---

## Stack técnico

- **Python** 3.12 · **Django** 5.2
- **Frontend**: Bootstrap 5 + HTMX + Chart.js (todo CDN, sin build step)
- **Base de datos**: SQLite
- **Servidor**: Gunicorn + WhiteNoise (sin nginx)
- **Deploy**: Kubernetes + Kustomize

## Estructura del proyecto

```
gym/            # Proyecto Django (settings/, urls.py)
apps/
  accounts/     # TrainerProfile, ClientProfile, mixins, CRUD usuarios
                #   management/commands/create_demo_data.py
  schedule/     # ClassType, GymClass, Booking + reservas HTMX
  training/     # TrainingPlan, PlanSection (inline formsets)
  messaging/    # Thread, Message + context_processor
  dashboard/    # Dashboards Chart.js (sin modelos propios)
templates/      # base_{client,trainer,admin}.html + templates por portal
static/         # CSS y JS del proyecto
k8s/            # Manifiestos Kubernetes (base + overlays dev/prod)
scripts/        # entrypoint.sh, backup-db.sh
```

## Ficheros de dependencias

| Fichero | Uso |
|---------|-----|
| `pyproject.toml` | Fuente de verdad — gestión con `uv` |
| `requirements.txt` | Producción — pip estándar |
| `requirements-dev.txt` | Desarrollo — pip estándar (incluye requirements.txt) |

## Documentación

- [`CLAUDE.md`](CLAUDE.md) — Referencia técnica rápida para desarrollo con Claude Code
- [`PLAN.md`](PLAN.md) — Arquitectura, decisiones de diseño y hoja de ruta
