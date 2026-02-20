# PLAN.md — GymAdmin

Documento de planificación y arquitectura del proyecto.
Describe qué se ha construido, por qué se tomaron las decisiones técnicas, y el camino a seguir.

---

## 1. Descripción del producto

**GymAdmin** es una aplicación web de administración para un gimnasio de entrenamiento funcional.
Diseñada para uso en escritorio y dispositivos móviles. Tres portales independientes según el rol.

### Roles de usuario

| Rol | `is_staff` | `is_superuser` | Descripción |
|-----|-----------|----------------|-------------|
| **Superadmin** | `True` | `True` | Gestión total: clientes, entrenadores, horarios, planes, mensajes. |
| **Entrenador** | `True` | `False` | Ve sus clases, gestiona sus planes, responde mensajes de sus clientes, tiene su dashboard. |
| **Cliente** | `False` | `False` | Reserva clases, consulta planes, envía mensajes, ve su historial. |

No se usa ningún campo adicional — la distinción se hace con los campos estándar de Django User.
La señal en `apps/accounts/signals.py` crea el perfil correspondiente al crear cada usuario.

### Funcionalidades implementadas (v0.2.0)

**Portal Cliente** (`/portal/client/`)
- Visualización del horario semanal con navegación por semanas (HTMX, sin recarga de página)
- Reserva y cancelación de plazas en clases (HTMX, actualiza solo la tarjeta)
- Historial personal de asistencia
- Visualización de planes de entrenamiento/dieta asignados
- Mensajería directa con el gimnasio (chat estilo inbox, HTMX)
- Dashboard personal: gráfico de asistencia y próximas reservas

**Portal Entrenador** (`/portal/trainer/`)
- Dashboard propio: KPIs (clases esta semana, clientes únicos, tasa de asistencia, planes activos) + gráfico de reservas en sus clases
- Horario semanal filtrado a sus clases con navegación HTMX
- Detalle de clase: lista de asistentes + marcar asistido / no se presentó
- CRUD de planes de entrenamiento para sus clientes (con inline formset de secciones)
- Inbox: mensajes de clientes que tienen reservas en sus clases
- Perfil editable (especialidad, bio, teléfono, avatar)

**Portal Superadmin** (`/portal/admin/`)
- CRUD completo de clientes (alta, edición, perfil, activar/desactivar)
- CRUD completo de entrenadores (alta, edición, perfil, vista de sus clases y planes)
- Gestión de tipos de clase y clases programadas (CRUD)
- Control de asistencia por clase
- Creación y asignación de planes de entrenamiento/dieta
- Bandeja de mensajes: todas las conversaciones
- Dashboard global: KPIs del gimnasio, gráfico de reservas semanales, clases más populares

**Datos de demo**
- Comando `python manage.py create_demo_data` (idempotente, soporta `--reset`)
- Crea: 1 superadmin, 3 entrenadores, 8 clientes, 4 tipos de clase, 36 clases (±2 semanas), ~215 reservas, 10 planes con secciones, 13 mensajes con respuestas

---

## 2. Decisiones de arquitectura

### ¿Por qué Django y no FastAPI?

FastAPI es ideal para APIs JSON puras consumidas por un frontend separado (React, Vue, app móvil).
Django es la elección correcta para este proyecto porque:

- **Templates server-side**: La app renderiza HTML en el servidor. Django tiene un motor de templates maduro e integrado.
- **ORM + migraciones**: Los modelos son relacionales. Django ORM abstrae SQL y `makemigrations` gestiona cambios de esquema automáticamente.
- **Autenticación integrada**: `is_staff`, `is_superuser`, sesiones, grupos, validación de contraseñas — todo de serie. Los tres roles se implementan sin ningún campo adicional.
- **Vistas genéricas CRUD**: `ListView`, `CreateView`, `UpdateView`, `DeleteView` generan el 80% del código repetitivo.
- **Admin Django**: Panel de emergencia para operaciones directas en DB (`/django-admin/`).
- **Formularios**: `ModelForm` e `inlineformset_factory` simplifican la edición de planes con secciones.

### ¿Por qué SQLite y no PostgreSQL?

Para esta demo, SQLite es suficiente y tiene ventajas claras:
- **Cero configuración**: No hay servidor de base de datos que gestionar.
- **Backup trivial**: Copiar el fichero `.sqlite3` es suficiente.
- **Sin dependencias externas**: El pod de Django contiene todo el stack.

**Limitación conocida**: SQLite no admite escrituras concurrentes desde múltiples procesos.
Por eso el despliegue en Kubernetes usa `replicas: 1` y `strategy: Recreate`.
Si en el futuro se necesita escalar, se migra a PostgreSQL con un pod separado.

### ¿Por qué HTMX y no React/Vue?

HTMX permite añadir dinamismo a las páginas (reservas sin recarga, navegación semanal, chat)
sin necesitar un build pipeline de JavaScript, ni gestionar un proyecto frontend separado.
Todo sigue siendo Python + templates Django. Para una demo, es la opción óptima.

### ¿Por qué WhiteNoise y no nginx?

WhiteNoise sirve los ficheros estáticos directamente desde el proceso Django/Gunicorn,
con compresión Brotli/gzip y cabeceras de caché correctas. Elimina la necesidad de
un sidecar de nginx en Kubernetes, simplificando el despliegue.

### ¿Por qué tres portales separados y no el admin de Django?

El admin de Django (`/django-admin/`) está diseñado para gestión interna de base de datos,
no para una UX de negocio. Los requisitos de dashboards con Chart.js, horario semanal,
mensajería y portal de entrenadores no encajan en el admin de Django. Se construyeron
portales propios con UX adecuada al negocio. El admin de Django se mantiene para emergencias.

### Estrategia de roles (sin campo adicional)

La distinción de roles usa los campos estándar de Django:

```python
# En cualquier vista:
if user.is_superuser:           # → Superadmin
elif user.is_staff:             # → Entrenador
else:                           # → Cliente
```

Los mixins de acceso encapsulan esta lógica y redirigen al portal correcto si el usuario
accede a un portal que no le corresponde (nunca se lanza 403 innecesariamente).

---

## 3. Estructura de ficheros

```
gymAdmin/
├── CLAUDE.md                       # Instrucciones para Claude Code
├── PLAN.md                         # Este documento
├── README.md                       # Guía de inicio rápido
├── pyproject.toml                  # Dependencias (uv)
├── uv.lock                         # Lock file de dependencias
├── .env.example                    # Plantilla de variables de entorno
├── Dockerfile                      # Imagen de producción
├── manage.py                       # CLI de Django
│
├── gym/                            # Paquete del proyecto Django
│   ├── urls.py                     # Router raíz: 3 portales + auth
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py             # Selecciona dev/prod por DJANGO_ENV
│       ├── base.py                 # Configuración compartida
│       ├── dev.py                  # DEBUG=True, debug_toolbar
│       └── prod.py                 # HSTS, SSL, cookies seguras
│
├── apps/
│   ├── accounts/                   # Usuarios, perfiles y mixins de acceso
│   │   ├── models.py               # TrainerProfile, ClientProfile
│   │   ├── signals.py              # Crea perfil según rol al crear usuario
│   │   ├── mixins.py               # SuperAdminRequiredMixin, TrainerRequiredMixin, ClientRequiredMixin
│   │   ├── forms.py                # TrainerCreate/Edit/ProfileForm + ClientCreate/Edit/ProfileForm
│   │   ├── admin.py                # CustomUserAdmin con perfiles inline
│   │   ├── apps.py                 # Registra señales en ready()
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── create_demo_data.py   # manage.py create_demo_data [--reset]
│   │   ├── urls/
│   │   │   ├── root.py             # portal_redirect: 3-way según rol
│   │   │   ├── client.py           # /portal/client/  (home, profile)
│   │   │   ├── trainer.py          # /portal/trainer/ (home, profile)
│   │   │   └── admin.py            # /portal/admin/   (client CRUD, trainer CRUD)
│   │   └── views/
│   │       ├── client.py           # ClientHomeView, ClientProfileView
│   │       ├── trainer.py          # TrainerHomeView, TrainerProfileView
│   │       └── admin.py            # AdminHomeView, Client*/Trainer* CRUD views
│   │
│   ├── schedule/                   # Horario y reservas
│   │   ├── models.py               # ClassType, GymClass, Booking
│   │   ├── forms.py                # ClassTypeForm, GymClassForm
│   │   ├── urls/
│   │   │   ├── client.py           # schedule, week_grid (HTMX), book, cancel, history
│   │   │   ├── trainer.py          # schedule, week_grid (HTMX), class_detail, mark_attendance
│   │   │   └── admin.py            # class CRUD, attendees, mark-attended, class_type CRUD
│   │   └── views/
│   │       ├── client.py           # ScheduleView, WeekGridPartialView, BookClassView, ...
│   │       ├── trainer.py          # TrainerScheduleView, TrainerWeekGridView, TrainerClassDetailView, ...
│   │       └── admin.py            # ClassListView, ClassCreateView, ClassUpdateView, ...
│   │
│   ├── training/                   # Planes de entrenamiento y dieta
│   │   ├── models.py               # TrainingPlan, PlanSection
│   │   ├── forms.py                # TrainingPlanForm, PlanSectionFormSet
│   │   ├── urls/
│   │   │   ├── client.py           # plan_list, plan_detail
│   │   │   ├── trainer.py          # plan_list, plan_detail, plan_create, plan_edit
│   │   │   └── admin.py            # plan CRUD completo
│   │   └── views/
│   │       ├── client.py           # PlanListView, PlanDetailView
│   │       ├── trainer.py          # TrainerPlan* (filtrado por created_by)
│   │       └── admin.py            # PlanListView, PlanCreateView, PlanEditView, PlanDeleteView
│   │
│   ├── messaging/                  # Mensajería
│   │   ├── models.py               # Thread (1:1 por cliente), Message
│   │   ├── context_processors.py   # unread_count + unread_admin_count → todos los templates
│   │   ├── urls/
│   │   │   ├── client.py           # inbox, send (HTMX), message_list (HTMX partial)
│   │   │   ├── trainer.py          # inbox (clientes del entrenador), thread_detail, reply
│   │   │   └── admin.py            # inbox (todos), thread_detail, reply
│   │   └── views/
│   │       ├── client.py           # ClientInboxView, SendMessageView, MessageListPartialView
│   │       ├── trainer.py          # TrainerInboxView, TrainerThreadDetailView, TrainerReplyView
│   │       └── admin.py            # AdminInboxView, ThreadDetailView, ReplyView
│   │
│   └── dashboard/                  # Sin modelos propios
│       ├── urls/
│       │   ├── client.py           # /portal/client/dashboard/
│       │   ├── trainer.py          # /portal/trainer/dashboard/
│       │   └── admin.py            # /portal/admin/dashboard/
│       └── views/
│           ├── client.py           # Asistencia personal, próximas clases, stats
│           ├── trainer.py          # KPIs entrenador, gráfico reservas en sus clases, próximas clases
│           └── admin.py            # KPIs globales, Chart.js (asistencia + popularidad)
│
├── templates/
│   ├── base.html                   # HTML base: Bootstrap 5 + HTMX CDN
│   ├── base_client.html            # Nav cliente (azul)
│   ├── base_trainer.html           # Nav entrenador (ámbar) + badge "ENTRENADOR"
│   ├── base_admin.html             # Nav superadmin (oscuro) + badge "SUPERADMIN"
│   ├── registration/login.html
│   ├── accounts/{client,trainer,admin}/
│   ├── schedule/{client,trainer,admin}/   # {client,trainer}/partials/: week_grid, class_card
│   ├── training/{client,trainer,admin}/
│   ├── messaging/{client,trainer,admin}/  # client/partials/: message_list
│   └── dashboard/{client,trainer,admin}/
│
├── static/
│   ├── css/gym.css                 # Overrides Bootstrap, estilos de formularios
│   └── js/gym.js                   # Auto-scroll mensajes, HTMX afterSwap hook
│
├── data/                           # SQLite (no en git)
│   └── db.sqlite3
│
├── scripts/
│   ├── entrypoint.sh               # migrate → gunicorn
│   └── backup-db.sh                # CronJob: cp db + retiene 30 backups
│
└── k8s/
    ├── base/
    │   ├── kustomization.yaml
    │   ├── namespace.yaml
    │   ├── configmap.yaml          # Variables no-secretas
    │   ├── configmap-backup-script.yaml  # Script inyectado en CronJob
    │   ├── pvc-db.yaml             # 1Gi para db.sqlite3
    │   ├── pvc-backup.yaml         # 5Gi para backups
    │   ├── deployment.yaml         # replicas:1, strategy:Recreate
    │   ├── service.yaml            # ClusterIP → puerto 80→8000
    │   └── cronjob-backup.yaml     # 0 3 * * * con busybox
    └── overlays/
        ├── dev/                    # Recursos mínimos, namespace gymadmin-dev
        └── prod/                   # Ingress TLS, recursos mayores, registry externo
```

---

## 4. Modelos y relaciones

```
User (Django built-in)
  ├── is_superuser=True → Superadmin (sin perfil extra)
  ├── is_staff=True, is_superuser=False → Entrenador
  │     └── TrainerProfile (1:1)      ← specialty, bio, phone, avatar
  └── is_staff=False → Cliente
        ├── ClientProfile (1:1)       ← goal, is_active_member, phone, avatar
        ├── bookings (1:N)            ← como cliente
        ├── message_thread (1:1)      ← solo clientes
        └── sent_messages (1:N)

User (is_staff=True)
  ├── taught_classes (1:N)            ← GymClass.instructor
  └── created_plans (1:N)             ← TrainingPlan.created_by

ClassType ──→ GymClass (1:N)
GymClass ──→ Booking (1:N)
User (cliente) ──→ Booking (1:N)

TrainingPlan ──→ PlanSection (1:N, ordenadas por `order`)
Thread ──→ Message (1:N, ordenadas por `sent_at`)
```

---

## 5. Flujos principales

### Reserva de clase (cliente)

```
Cliente visita /portal/client/schedule/
  → ScheduleView calcula semana actual y clases
  → Template renderiza week_grid con class_card para cada clase
  → Botón "Reservar": hx-post a /portal/client/schedule/book/<pk>/
  → BookClassView: valida aforo → crea/actualiza Booking(status="confirmed")
  → Devuelve class_card actualizada (HTMX outerHTML swap)
```

### Navegación semanal (HTMX — cliente y entrenador)

```
Click "Siguiente":
  → hx-get a /portal/{client|trainer}/schedule/week/?week=1
  → WeekGridView calcula semana offset=1, filtra por entrenador si aplica
  → Devuelve week_grid.html parcial
  → HTMX sustituye innerHTML de #week-grid
```

### Asistencia de clase (entrenador)

```
Entrenador visita /portal/trainer/schedule/class/<pk>/
  → TrainerClassDetailView: verifica que cls.instructor == request.user
  → Lista de bookings confirmados/asistidos/no_show
  → POST a mark_attendance/<pk>/<booking_pk>/
  → Cambia booking.status → redirect a class_detail
```

### Mensajería cliente ↔ staff

```
Cliente escribe mensaje → hx-post a /portal/client/messages/send/
  → SendMessageView: Message(is_read_by_admin=False, sender=cliente)
  → Thread.save() actualiza updated_at
  → Devuelve message_list.html parcial

Entrenador responde → POST a /portal/trainer/messages/<thread_pk>/reply/
  → TrainerReplyView: Message(is_read_by_client=False, sender=entrenador)
  → redirect a thread_detail
```

### Redirección post-login (3 vías)

```
/auth/login/ → portal_redirect view
  → user.is_superuser?  → redirect("admin_dashboard:dashboard")
  → user.is_staff?      → redirect("trainer_dashboard:dashboard")
  → else                → redirect("client_dashboard:dashboard")
```

### Creación de entrenador (superadmin)

```
Superadmin → /portal/admin/trainers/create/
  → TrainerCreateForm: User con is_staff=True, is_superuser=False
  → user.save() → señal post_save → TrainerProfile.objects.get_or_create(user=user)
  → TrainerCreateView actualiza los campos del perfil
  → redirect a trainer_detail
```

---

## 6. Gestión de la base de datos por entorno

### Local (desarrollo)

```bash
# Primera vez / reset completo
.venv/bin/python manage.py migrate
.venv/bin/python manage.py create_demo_data   # crea todos los datos de prueba

# Tras cambiar un modelo
.venv/bin/python manage.py makemigrations <app>
.venv/bin/python manage.py migrate

# Backup manual
cp data/db.sqlite3 "data/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"

# Reset total con datos de demo
rm data/db.sqlite3
.venv/bin/python manage.py migrate
.venv/bin/python manage.py create_demo_data
```

### Docker

```bash
# Ejecutar con datos persistentes
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="dev-secret" \
  -e DJANGO_ENV=dev \
  -v "$(pwd)/data:/app/data" \
  gymadmin:dev

# Los datos de demo se pueden cargar dentro del contenedor
docker exec -it <container_id> /bin/sh
.venv/bin/python manage.py create_demo_data
```

### Kubernetes

```bash
kubectl exec -n gymadmin-dev -it deployment/gymadmin -- /bin/sh
.venv/bin/python manage.py create_demo_data

# Backup manual
kubectl create job \
  --from=cronjob/gymadmin-db-backup \
  "backup-manual-$(date +%Y%m%d)" \
  -n gymadmin-dev

# Restaurar backup
cp /app/backups/db_FECHA.sqlite3 /app/data/db.sqlite3
exit
kubectl rollout restart deployment/gymadmin -n gymadmin-dev
```

### Tabla comparativa

| Aspecto | Local | Docker | Kubernetes |
|---------|-------|--------|------------|
| Fichero | `data/db.sqlite3` | `/app/data/db.sqlite3` | `/app/data/db.sqlite3` en PVC |
| Persistencia | Siempre (carpeta local) | Solo con `-v` | Siempre (PVC) |
| Migraciones | Manual (`migrate`) | Automática (entrypoint) | Automática (entrypoint) |
| Backup | Manual (cp) | Manual (cp del volumen) | Automático 03:00 AM |
| Demo data | `create_demo_data` | `docker exec` + comando | `kubectl exec` + comando |

---

## 7. Despliegue en Kubernetes

### Diagrama

```
Internet
  │
  └─ Ingress (nginx + cert-manager TLS) [solo prod]
       │
       └─ Service (ClusterIP, port 80→8000)
            │
            └─ Pod: gymadmin
                 │  image: gymadmin:latest
                 │  gunicorn (2 workers)
                 │  WhiteNoise (estáticos)
                 │
                 ├── PVC: gymadmin-db-pvc (1Gi)
                 │    └── /app/data/db.sqlite3
                 │
                 └── PVC: gymadmin-backup-pvc (5Gi)
                      └── /app/backups/db_YYYYMMDD_HHmmss.sqlite3 (×30 máx)

CronJob: gymadmin-db-backup
  schedule: 0 3 * * *
  image: busybox
  mounts: pvc-db (read-only) + pvc-backup (write)
  action: cp db.sqlite3 → backups/ + limpia los más antiguos de 30
```

### Overlays

| Overlay | Namespace        | Imagen              | Recursos    |
|---------|------------------|---------------------|-------------|
| `dev`   | `gymadmin-dev`   | `gymadmin:dev`      | Mínimos     |
| `prod`  | `gymadmin-prod`  | `registry/gymadmin` | Estándar    |

### Secret requerido

```bash
kubectl create secret generic gymadmin-secret \
  --namespace gymadmin-dev \
  --from-literal=DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
```

---

## 8. Hoja de ruta — próximas iteraciones

### ✅ Implementado (v0.2.0)

- [x] **Tres roles** (Superadmin / Entrenador / Cliente) con portales independientes
- [x] **TrainerProfile**: perfil con especialidad, bio, avatar
- [x] **Portal entrenador**: dashboard, horario propio, gestión de asistencia, planes, mensajes
- [x] **CRUD entrenadores** en panel superadmin
- [x] **Datos de demo**: comando idempotente con entrenadores, clientes, clases, reservas, planes y mensajes

### v0.3 — Mejoras de UX y completitud

- [ ] **Lista de espera**: cuando se cancela una reserva, notificar al siguiente en la lista.
- [ ] **Clases recurrentes**: plantillas semanales para no crear cada clase manualmente.
- [ ] **Perfil de cliente enriquecido**: peso, altura, historial de mediciones.
- [ ] **Notificaciones por email**: al cliente cuando el entrenador responde o asigna un plan.
- [ ] **Filtros en dashboards**: seleccionar rango de fechas para los gráficos.
- [ ] **Password reset**: flujo completo de recuperación de contraseña en portal cliente.

### v1.0 — Producción real

- [ ] **Migrar a PostgreSQL**: necesario para más de 1 réplica. Cambios: `requirements` añade `psycopg`, settings actualiza `DATABASES`, PVC pasa a StatefulSet o RDS/Cloud SQL.
- [ ] **Almacenamiento de media en S3/GCS**: los avatares en PVC local no son adecuados para producción multi-réplica.
- [ ] **CI/CD**: pipeline en GitHub Actions → build Docker → push registry → `kubectl apply`.
- [ ] **API REST**: añadir DRF para exponer endpoints a una futura app móvil.
- [ ] **Pagos**: integración con Stripe para gestionar suscripciones.
- [ ] **App móvil**: React Native o Flutter consumiendo la API REST.

---

## 9. Guía de contribución

### Añadir una nueva sección al portal cliente

1. Definir el modelo en la app correspondiente (o crear nueva app bajo `apps/`).
2. `makemigrations <app>` + `migrate`.
3. Crear `urls/client.py` con las rutas.
4. Crear `views/client.py` con vistas que hereden de `ClientRequiredMixin`.
5. Crear templates en `templates/<app>/client/`.
6. Registrar las URLs en `gym/urls.py`.
7. Añadir enlace en `templates/base_client.html`.

### Añadir una nueva sección al portal entrenador

Mismo proceso pero con `TrainerRequiredMixin`, `urls/trainer.py`, `views/trainer.py`,
templates en `templates/<app>/trainer/`, y enlace en `templates/base_trainer.html`.

### Añadir una nueva sección al portal superadmin

Mismo proceso pero con `SuperAdminRequiredMixin`, `urls/admin.py`, `views/admin.py`,
templates en `templates/<app>/admin/`, y enlace en `templates/base_admin.html`.

### Añadir un endpoint HTMX

1. Crear la vista en el fichero `views/*.py` correspondiente.
2. La vista devuelve `HttpResponse(html)` donde `html` es un template parcial renderizado.
3. El template parcial va en `templates/<app>/<portal>/partials/`.
4. Registrar la URL.
5. En el template HTML, usar `hx-get`/`hx-post` + `hx-target` + `hx-swap`.

### Convenciones de código

- Clases de vista: usar genéricas de Django (`TemplateView`, `ListView`, `CreateView`…).
- No usar decoradores funcionales de login — siempre mixins en las clases.
- Los forms que combinan múltiples modelos usan `View` directamente (más control).
- Nombres de template: `snake_case.html`, misma nomenclatura que el modelo o acción.
- Los mensajes flash usan `messages.success/warning/error` de `django.contrib.messages`.
- Nunca importar `StaffRequiredMixin` en código nuevo — usar `SuperAdminRequiredMixin`.
