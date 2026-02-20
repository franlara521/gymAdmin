# CLAUDE.md — GymAdmin

Aplicación web de administración para un gimnasio de entrenamiento funcional.
Demo en Python/Django con despliegue en Kubernetes.

## Stack

- **Backend:** Django 5.2, Python 3.12
- **Frontend:** Templates Django + Bootstrap 5 + HTMX + Chart.js (todo CDN)
- **Base de datos:** SQLite (`data/db.sqlite3`)
- **Servidor:** Gunicorn + WhiteNoise (sin nginx sidecar)
- **Gestión de paquetes:** `uv` (`.venv/bin/python`)
- **Deploy:** Kubernetes con Kustomize (`k8s/base/`, `k8s/overlays/dev/`, `k8s/overlays/prod/`)

## Roles de usuario

| Rol | `is_staff` | `is_superuser` | Perfil | Portal |
|-----|-----------|----------------|--------|--------|
| Superadmin | `True` | `True` | — | `/portal/admin/` |
| Entrenador | `True` | `False` | `TrainerProfile` | `/portal/trainer/` |
| Cliente | `False` | `False` | `ClientProfile` | `/portal/client/` |

No se usa ningún campo adicional — la distinción se hace con los campos estándar de Django User.

## Estructura del proyecto

```
gym/                    # Proyecto Django (settings/, urls.py, wsgi.py)
  settings/
    base.py             # Configuración compartida
    dev.py              # DEBUG=True, debug_toolbar habilitado
    prod.py             # HSTS, SSL, cookies seguras
apps/
  accounts/             # ClientProfile, TrainerProfile, mixins, CRUD clientes+entrenadores
    management/
      commands/
        create_demo_data.py  # python manage.py create_demo_data
  schedule/             # ClassType, GymClass, Booking + reservas HTMX
  training/             # TrainingPlan, PlanSection (formsets inline)
  messaging/            # Thread, Message + context_processor de no-leídos
  dashboard/            # Solo vistas con Chart.js (sin modelos propios)
templates/              # Templates globales organizados por app/portal
  base.html             # Bootstrap 5 + HTMX CDN
  base_client.html      # nav azul (cliente)
  base_admin.html       # nav oscuro + badge SUPERADMIN
  base_trainer.html     # nav ámbar + badge ENTRENADOR
static/                 # CSS y JS del proyecto
k8s/                    # Manifiestos Kubernetes
scripts/                # entrypoint.sh, backup-db.sh
```

## Portales y namespaces de URL

| Portal        | Prefijo URL                        | Namespace            |
|---------------|------------------------------------|----------------------|
| Cliente       | `/portal/client/`                  | `client`             |
| Entrenador    | `/portal/trainer/`                 | `trainer`            |
| Superadmin    | `/portal/admin/`                   | `gym_admin`          |
| Schedule cli  | `/portal/client/schedule/`         | `client_schedule`    |
| Schedule tra  | `/portal/trainer/schedule/`        | `trainer_schedule`   |
| Schedule adm  | `/portal/admin/schedule/`          | `admin_schedule`     |
| Training cli  | `/portal/client/training/`         | `client_training`    |
| Training tra  | `/portal/trainer/training/`        | `trainer_training`   |
| Training adm  | `/portal/admin/training/`          | `admin_training`     |
| Mensajes cli  | `/portal/client/messages/`         | `client_messaging`   |
| Mensajes tra  | `/portal/trainer/messages/`        | `trainer_messaging`  |
| Mensajes adm  | `/portal/admin/messages/`          | `admin_messaging`    |
| Dashboard cli | `/portal/client/dashboard/`        | `client_dashboard`   |
| Dashboard tra | `/portal/trainer/dashboard/`       | `trainer_dashboard`  |
| Dashboard adm | `/portal/admin/dashboard/`         | `admin_dashboard`    |
| Auth Django   | `/auth/`                           | —                    |
| Django admin  | `/django-admin/`                   | —                    |

## Control de acceso

Mixins en `apps/accounts/mixins.py`:
- `SuperAdminRequiredMixin` — requiere `is_superuser=True`. Redirige entrenadores a su portal y clientes al suyo.
- `TrainerRequiredMixin` — requiere `is_staff=True, is_superuser=False`. Redirige superadmins y clientes a su portal.
- `ClientRequiredMixin` — requiere `is_staff=False, is_superuser=False`. Redirige staff a su portal.
- `StaffRequiredMixin` — alias de `SuperAdminRequiredMixin` (compatibilidad).

Regla: **toda vista hereda del mixin correspondiente a su portal**.

## Estructura de cada app

```
apps/<app>/
  models.py
  forms.py
  admin.py
  apps.py
  urls/
    client.py    # URLs portal cliente
    trainer.py   # URLs portal entrenador
    admin.py     # URLs portal superadmin
  views/
    client.py    # Vistas portal cliente
    trainer.py   # Vistas portal entrenador
    admin.py     # Vistas portal superadmin
  migrations/
```

`apps/dashboard/` no tiene `models.py` (solo vistas que agregan datos de otras apps).

## Convenciones de templates

```
templates/
  base.html               # Bootstrap 5 + HTMX CDN
  base_client.html        # extends base, nav azul cliente
  base_trainer.html       # extends base, nav ámbar entrenador
  base_admin.html         # extends base, nav oscuro superadmin
  <app>/client/           # Templates portal cliente
  <app>/trainer/          # Templates portal entrenador
  <app>/admin/            # Templates portal superadmin
  <app>/client/partials/  # Parciales HTMX cliente
  <app>/trainer/partials/ # Parciales HTMX entrenador
```

## Modelos principales

```python
# accounts
TrainerProfile(user OneToOne→staff, phone, specialty, bio, avatar, joined_at)
ClientProfile(user OneToOne, phone, date_of_birth, join_date, goal, notes, is_active_member, avatar)

# schedule
ClassType(name, description, default_duration_minutes, color)
GymClass(class_type FK, instructor FK(staff), start_datetime, end_datetime, capacity, is_cancelled)
  → props: spots_available, is_full, confirmed_count
Booking(client FK, gym_class FK, status, booked_at) unique_together(client, gym_class)

# training
TrainingPlan(title, plan_type, created_by FK(staff), assigned_to FK(client), is_active)
PlanSection(plan FK, title, order, content)

# messaging
Thread(client OneToOne)  → props: unread_by_admin_count, unread_by_client_count, last_message
Message(thread FK, sender FK, body, is_read_by_admin, is_read_by_client)
```

## Context processor

`apps/messaging/context_processors.unread_count` inyecta en todos los templates:
- `unread_count` — mensajes sin leer para el cliente
- `unread_admin_count` — hilos con mensajes sin leer para el staff (admin o entrenador)

## Interacciones HTMX clave

| Endpoint                              | Target              | Swap        |
|---------------------------------------|---------------------|-------------|
| `client_schedule:week_grid`           | `#week-grid`        | `innerHTML` |
| `trainer_schedule:week_grid`          | `#week-grid`        | `innerHTML` |
| `client_schedule:book` (POST)         | `#class-card-{pk}`  | `outerHTML` |
| `client_schedule:cancel` (POST)       | `#class-card-{pk}`  | `outerHTML` |
| `client_messaging:send` (POST)        | `#message-list`     | `innerHTML` |

## Base de datos por entorno

| Entorno | Ubicación del fichero | Persistencia | Backup |
|---------|----------------------|--------------|--------|
| Local | `data/db.sqlite3` | Carpeta local (git-ignored) | Manual: `cp data/db.sqlite3 data/db_YYYYMMDD.sqlite3` |
| Docker | `/app/data/db.sqlite3` | Volumen montado con `-v $(pwd)/data:/app/data` | Copiar el volumen montado |
| Kubernetes | `/app/data/db.sqlite3` en PVC `gymadmin-db-pvc` | PersistentVolumeClaim 1Gi | CronJob automático a las 3AM → `/app/backups/` |

## Kubernetes — reglas críticas

- `replicas: 1` y `strategy: Recreate` son **obligatorios** con SQLite.
- PVC `gymadmin-db-pvc` → `/app/data/db.sqlite3`
- PVC `gymadmin-backup-pvc` → `/app/backups/` (CronJob a las 3AM, retiene 30 copias)
- El Secret `gymadmin-secret` debe contener `DJANGO_SECRET_KEY`.

## Variables de entorno

| Variable               | Descripción                          | Default dev        |
|------------------------|--------------------------------------|--------------------|
| `DJANGO_ENV`           | `dev` o `prod`                       | `dev`              |
| `DJANGO_SECRET_KEY`    | Clave secreta Django                 | *(en dev settings)*|
| `DJANGO_ALLOWED_HOSTS` | Hosts separados por coma             | `*` en dev         |
| `DB_PATH`              | Ruta absoluta al fichero SQLite      | `data/db.sqlite3`  |
| `MEDIA_ROOT`           | Directorio de uploads (avatares)     | `media/`           |

## Comandos frecuentes

```bash
# Desarrollo
.venv/bin/python manage.py runserver
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check

# Datos de demo (idempotente)
.venv/bin/python manage.py create_demo_data
.venv/bin/python manage.py create_demo_data --reset   # limpia y regenera

# Tests
.venv/bin/pytest

# Docker — construir y ejecutar con datos persistentes
docker build -t gymadmin:dev .
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="dev-secret" -e DJANGO_ENV=dev \
  -v "$(pwd)/data:/app/data" gymadmin:dev

# Kubernetes — primer despliegue
kubectl create namespace gymadmin-dev
kubectl create secret generic gymadmin-secret \
  --namespace gymadmin-dev \
  --from-literal=DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
kubectl apply -k k8s/overlays/dev/

# Kubernetes — actualizar tras cambios de código
kubectl rollout restart deployment/gymadmin -n gymadmin-dev

# Kubernetes — shell en el pod
kubectl exec -n gymadmin-dev -it deployment/gymadmin -- /bin/sh

# Kubernetes (prod)
kubectl apply -k k8s/overlays/prod/
```

## Usuarios de demo

| Usuario | Contraseña | Rol | Portal |
|---------|-----------|-----|--------|
| `admin` | `admin1234` | Superadmin | `/portal/admin/` |
| `ana.garcia` | `trainer1234` | Entrenadora (CrossFit) | `/portal/trainer/` |
| `marcos.herrero` | `trainer1234` | Entrenador (HIIT+Fuerza) | `/portal/trainer/` |
| `laura.sanchez` | `trainer1234` | Entrenadora (Yoga) | `/portal/trainer/` |
| `carlos.ruiz` | `client1234` | Cliente | `/portal/client/` |
| `elena.martin` | `client1234` | Cliente | `/portal/client/` |
| *(+6 clientes)* | `client1234` | Cliente | `/portal/client/` |

## Notas de desarrollo

- La señal en `apps/accounts/signals.py` crea `TrainerProfile` si `is_staff=True, is_superuser=False`, y `ClientProfile` si `is_staff=False`.
- Los superadmins creados con `createsuperuser` llegan a `/portal/admin/`.
- `StaffRequiredMixin` es alias de `SuperAdminRequiredMixin` (para compatibilidad con código existente).
- En dev, `django-debug-toolbar` está activo en la barra lateral.
- WhiteNoise sirve los estáticos directamente desde Django.
