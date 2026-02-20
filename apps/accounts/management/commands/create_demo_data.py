"""
Comando de gestión para crear datos de demostración.

Uso:
    .venv/bin/python manage.py create_demo_data
    .venv/bin/python manage.py create_demo_data --reset  # limpia datos demo primero
"""
import random
from datetime import timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


TRAINERS = [
    {
        "username": "ana.garcia",
        "first_name": "Ana",
        "last_name": "García",
        "email": "ana.garcia@gymadmin.demo",
        "password": "trainer1234",
        "specialty": "crossfit",
        "bio": "Especialista en CrossFit con 8 años de experiencia. Certificada Level 2.",
        "phone": "612 345 678",
    },
    {
        "username": "marcos.herrero",
        "first_name": "Marcos",
        "last_name": "Herrero",
        "email": "marcos.herrero@gymadmin.demo",
        "password": "trainer1234",
        "specialty": "hiit",
        "bio": "Entrenador personal especializado en HIIT y entrenamiento de fuerza. 5 años de experiencia.",
        "phone": "623 456 789",
    },
    {
        "username": "laura.sanchez",
        "first_name": "Laura",
        "last_name": "Sánchez",
        "email": "laura.sanchez@gymadmin.demo",
        "password": "trainer1234",
        "specialty": "yoga",
        "bio": "Instructora de Yoga certificada. Formada en Hatha y Vinyasa. Apasionada del bienestar integral.",
        "phone": "634 567 890",
    },
]

CLIENTS = [
    {"username": "carlos.ruiz", "first_name": "Carlos", "last_name": "Ruiz", "email": "carlos.ruiz@demo.com", "goal": "muscle_gain"},
    {"username": "elena.martin", "first_name": "Elena", "last_name": "Martín", "email": "elena.martin@demo.com", "goal": "weight_loss"},
    {"username": "pablo.lopez", "first_name": "Pablo", "last_name": "López", "email": "pablo.lopez@demo.com", "goal": "endurance"},
    {"username": "sara.gonzalez", "first_name": "Sara", "last_name": "González", "email": "sara.gonzalez@demo.com", "goal": "general"},
    {"username": "miguel.fernandez", "first_name": "Miguel", "last_name": "Fernández", "email": "miguel.fernandez@demo.com", "goal": "muscle_gain"},
    {"username": "lucia.diaz", "first_name": "Lucía", "last_name": "Díaz", "email": "lucia.diaz@demo.com", "goal": "weight_loss"},
    {"username": "jorge.perez", "first_name": "Jorge", "last_name": "Pérez", "email": "jorge.perez@demo.com", "goal": "endurance"},
    {"username": "marta.romero", "first_name": "Marta", "last_name": "Romero", "email": "marta.romero@demo.com", "goal": "general"},
]

CLASS_TYPES = [
    {"name": "CrossFit Matutino", "description": "Entrenamiento funcional de alta intensidad en grupo.", "default_duration_minutes": 60, "color": "#e74c3c"},
    {"name": "HIIT Express", "description": "Intervalos de alta intensidad en 45 minutos.", "default_duration_minutes": 45, "color": "#e67e22"},
    {"name": "Yoga Restaurativo", "description": "Sesión de yoga para recuperación y movilidad.", "default_duration_minutes": 75, "color": "#27ae60"},
    {"name": "Fuerza y Movilidad", "description": "Trabajo de fuerza con énfasis en movilidad articular.", "default_duration_minutes": 60, "color": "#2980b9"},
]

MESSAGES = [
    ("carlos.ruiz", "ana.garcia", "Hola Ana! Tengo una duda sobre la técnica del clean & jerk, ¿podrías ayudarme?"),
    ("elena.martin", "ana.garcia", "Buenos días! Esta semana no podré ir el jueves, ¿hay alguna clase alternativa?"),
    ("pablo.lopez", "marcos.herrero", "Marcos, ¿puedo añadir más series de sentadillas a mi plan? Me siento con energía."),
    ("sara.gonzalez", "marcos.herrero", "Hola! ¿Cuántos días a la semana me recomiendas entrenar para perder peso?"),
    ("miguel.fernandez", "ana.garcia", "¿El CrossFit de mañana es especialmente exigente? Llevo dos días con agujetas."),
    ("lucia.diaz", "laura.sanchez", "¡Me encantó la clase de ayer! ¿Cuándo es la próxima sesión de yoga restaurativo?"),
    ("jorge.perez", "marcos.herrero", "Oye Marcos, ¿tienes algún consejo para mejorar mi resistencia en el HIIT?"),
    ("marta.romero", "laura.sanchez", "Laura, ¿el yoga es adecuado para principiantes? Nunca he probado."),
]

TRAINER_REPLIES = {
    "ana.garcia": [
        "¡Claro! La próxima semana te dedico unos minutos antes de clase para trabajarlo.",
        "No te preocupes, el viernes tienes CrossFit Matutino a las 9:00, ¡te esperamos!",
        "Descansa bien hoy, mañana la clase es de intensidad media. ¡Puedes!",
    ],
    "marcos.herrero": [
        "¡Perfecto! Añade 2 series más pero controla la técnica. Actualizo tu plan esta semana.",
        "Para pérdida de peso te recomiendo 3-4 días de HIIT combinados con algo de fuerza. ¡Hablamos!",
        "Trabaja la respiración: inhala en la fase de baja intensidad, exhala en la alta. Marcará la diferencia.",
    ],
    "laura.sanchez": [
        "¡Qué alegría! La próxima sesión es el jueves a las 18:30. ¡Te espero!",
        "El yoga es perfecto para principiantes. Empieza con la clase restaurativa, es más suave. 🙏",
    ],
}


class Command(BaseCommand):
    help = "Crea datos de demostración: superadmin, entrenadores, clientes, clases y planes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los datos de demo antes de crearlos de nuevo.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        self.stdout.write(self.style.MIGRATE_HEADING("=== Creando datos de demostración ==="))

        admin_user = self._create_superadmin()
        trainer_users = self._create_trainers()
        client_users = self._create_clients()
        class_types = self._create_class_types()
        classes = self._create_classes(class_types, trainer_users)
        self._create_bookings(classes, client_users)
        self._create_plans(trainer_users, client_users)
        self._create_messages(client_users, trainer_users)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Datos de demostración creados correctamente.\n"))
        self.stdout.write("  Superadmin:   admin / admin1234")
        self.stdout.write("  Entrenadores: ana.garcia, marcos.herrero, laura.sanchez / trainer1234")
        self.stdout.write("  Clientes:     carlos.ruiz, elena.martin, … / client1234")

    def _reset(self):
        from apps.accounts.models import TrainerProfile, ClientProfile
        from apps.schedule.models import ClassType, GymClass, Booking
        from apps.training.models import TrainingPlan
        from apps.messaging.models import Thread

        demo_usernames = (
            ["admin"]
            + [t["username"] for t in TRAINERS]
            + [c["username"] for c in CLIENTS]
        )
        User.objects.filter(username__in=demo_usernames).delete()
        self.stdout.write(self.style.WARNING("  → Datos previos eliminados."))

    def _create_superadmin(self):
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "GymAdmin",
                "email": "admin@gymadmin.demo",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password("admin1234")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        if created:
            self.stdout.write(f"  + Superadmin creado: admin")
        else:
            self.stdout.write(f"  · Superadmin ya existe (contraseña actualizada): admin")
        return user

    def _create_trainers(self):
        from apps.accounts.models import TrainerProfile

        trainer_users = []
        for data in TRAINERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "is_staff": True,
                    "is_superuser": False,
                },
            )
            user.set_password(data["password"])
            user.is_staff = True
            user.is_superuser = False
            user.save()
            if created:
                # La señal crea el TrainerProfile automáticamente
                self.stdout.write(f"  + Entrenador creado: {data['username']}")
            else:
                self.stdout.write(f"  · Entrenador ya existe (contraseña actualizada): {data['username']}")

            # Actualizar perfil
            profile, _ = TrainerProfile.objects.get_or_create(user=user)
            profile.specialty = data["specialty"]
            profile.bio = data["bio"]
            profile.phone = data["phone"]
            profile.save()

            trainer_users.append(user)
        return trainer_users

    def _create_clients(self):
        from apps.accounts.models import ClientProfile

        client_users = []
        for data in CLIENTS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            user.set_password("client1234")
            user.is_staff = False
            user.is_superuser = False
            user.save()
            if created:
                self.stdout.write(f"  + Cliente creado: {data['username']}")
            else:
                self.stdout.write(f"  · Cliente ya existe (contraseña actualizada): {data['username']}")

            profile, _ = ClientProfile.objects.get_or_create(user=user)
            profile.goal = data["goal"]
            profile.is_active_member = True
            profile.save()

            client_users.append(user)
        return client_users

    def _create_class_types(self):
        from apps.schedule.models import ClassType

        types = []
        for data in CLASS_TYPES:
            ct, created = ClassType.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "default_duration_minutes": data["default_duration_minutes"],
                    "color": data["color"],
                },
            )
            if created:
                self.stdout.write(f"  + Tipo de clase: {data['name']}")
            types.append(ct)
        return types

    def _create_classes(self, class_types, trainer_users):
        from apps.schedule.models import GymClass

        # crossfit → ana (índice 0), hiit/fuerza → marcos (índice 1), yoga → laura (índice 2)
        type_trainer_map = {
            class_types[0]: trainer_users[0],  # CrossFit → Ana
            class_types[1]: trainer_users[1],  # HIIT → Marcos
            class_types[2]: trainer_users[2],  # Yoga → Laura
            class_types[3]: trainer_users[1],  # Fuerza → Marcos
        }

        # Horarios: hora_inicio, día_semana (0=lunes)
        schedule_template = [
            (class_types[0], 0, 9),   # CrossFit Lunes 9h
            (class_types[0], 2, 9),   # CrossFit Miércoles 9h
            (class_types[0], 4, 9),   # CrossFit Viernes 9h
            (class_types[1], 1, 7),   # HIIT Martes 7h
            (class_types[1], 3, 7),   # HIIT Jueves 7h
            (class_types[2], 1, 18),  # Yoga Martes 18h
            (class_types[2], 4, 18),  # Yoga Viernes 18h
            (class_types[3], 0, 18),  # Fuerza Lunes 18h
            (class_types[3], 3, 18),  # Fuerza Jueves 18h
        ]

        today = timezone.localdate()
        monday_this_week = today - timedelta(days=today.weekday())

        all_classes = []
        for week_offset in [-2, -1, 0, 1]:  # 2 semanas atrás, esta semana, próxima
            monday = monday_this_week + timedelta(weeks=week_offset)
            for ct, weekday, hour in schedule_template:
                class_date = monday + timedelta(days=weekday)
                start_dt = timezone.make_aware(
                    timezone.datetime(class_date.year, class_date.month, class_date.day, hour, 0)
                )
                end_dt = start_dt + timedelta(minutes=ct.default_duration_minutes)
                instructor = type_trainer_map[ct]

                cls, created = GymClass.objects.get_or_create(
                    class_type=ct,
                    instructor=instructor,
                    start_datetime=start_dt,
                    defaults={
                        "end_datetime": end_dt,
                        "capacity": random.choice([10, 12, 15]),
                        "is_cancelled": False,
                    },
                )
                all_classes.append(cls)

        self.stdout.write(f"  + {GymClass.objects.count()} clases en total")
        return all_classes

    def _create_bookings(self, classes, client_users):
        from apps.schedule.models import Booking

        now = timezone.now()
        booking_count = 0
        for cls in classes:
            # Asignar entre 3 y 8 clientes aleatorios a cada clase
            attendees = random.sample(client_users, min(random.randint(3, 8), len(client_users)))
            for client in attendees:
                is_past = cls.start_datetime < now
                if is_past:
                    status = random.choices(
                        ["attended", "no_show", "confirmed"],
                        weights=[65, 15, 20],
                    )[0]
                else:
                    status = "confirmed"

                _, created = Booking.objects.get_or_create(
                    client=client,
                    gym_class=cls,
                    defaults={"status": status},
                )
                if created:
                    booking_count += 1

        self.stdout.write(f"  + {booking_count} reservas creadas")

    def _create_plans(self, trainer_users, client_users):
        from apps.training.models import TrainingPlan, PlanSection

        plan_data = [
            {
                "trainer": trainer_users[0],  # Ana
                "clients": client_users[:3],
                "title": "Plan CrossFit Base",
                "plan_type": "training",
                "sections": [
                    ("Calentamiento", "10 min de remo o bicicleta estática.\n3 rondas:\n- 10 air squats\n- 10 push-ups\n- 10 pull-aparts con banda"),
                    ("WOD Principal", "AMRAP 20 minutos:\n- 5 pull-ups\n- 10 push-ups\n- 15 air squats\n\nEscalar según nivel."),
                    ("Enfriamiento", "5 min de caminar.\nEstiramiento de cadera, hombros y espalda.\nFoam rolling en piernas."),
                ],
            },
            {
                "trainer": trainer_users[1],  # Marcos
                "clients": client_users[2:6],
                "title": "Plan HIIT + Fuerza 4 semanas",
                "plan_type": "combined",
                "sections": [
                    ("Semana 1-2: Base aeróbica", "Lunes/Miércoles/Viernes:\n- HIIT 20 min (trabajo:descanso 30s:30s)\n- Fuerza 30 min (sentadilla, peso muerto, press)\n\nMartes/Jueves:\n- Caminar 30 min o descanso activo."),
                    ("Semana 3-4: Intensidad", "Mismos días pero:\n- HIIT aumenta a 25 min (ratio 40s:20s)\n- Añadir 1 serie extra en cada ejercicio de fuerza\n- Progresión de peso del 5-10%."),
                    ("Nutrición y recuperación", "Proteína: 1.6-2g por kg de peso corporal.\nHidratos de calidad: avena, arroz, boniato.\nDormir 7-9 horas.\nEstiramiento post-entreno obligatorio."),
                ],
            },
            {
                "trainer": trainer_users[2],  # Laura
                "clients": client_users[5:8],
                "title": "Programa Yoga Restaurativo 6 semanas",
                "plan_type": "training",
                "sections": [
                    ("Semanas 1-2: Fundamentos", "Posturas clave: Balasana, Viparita Karani, Supta Baddha Konasana.\n30-40 min por sesión.\nRespira profundo, mantén cada postura 5-10 respiraciones."),
                    ("Semanas 3-4: Movilidad de cadera", "Añadir: Pigeon Pose, Lizard Pose, Reclined Butterfly.\nIncorporar meditación guiada 10 min al final.\nJournal: anota cómo te sientes antes/después."),
                    ("Semanas 5-6: Integración", "Sesión completa de 60 min.\nSaludo al sol suave × 5.\nSecuencia restaurativa personalizada.\nSavasana 15 min con música relajante."),
                ],
            },
        ]

        for pd in plan_data:
            for client in pd["clients"]:
                plan, created = TrainingPlan.objects.get_or_create(
                    title=pd["title"],
                    assigned_to=client,
                    created_by=pd["trainer"],
                    defaults={"plan_type": pd["plan_type"], "is_active": True},
                )
                if created:
                    for i, (title, content) in enumerate(pd["sections"], start=1):
                        PlanSection.objects.get_or_create(
                            plan=plan,
                            order=i,
                            defaults={"title": title, "content": content},
                        )

        self.stdout.write(f"  + {TrainingPlan.objects.count()} planes creados")

    def _create_messages(self, client_users, trainer_users):
        from apps.messaging.models import Thread, Message

        # Mapear username → user
        user_by_username = {u.username: u for u in list(client_users) + list(trainer_users)}

        msg_count = 0
        for client_username, trainer_username, body in MESSAGES:
            client_user = user_by_username.get(client_username)
            trainer_user = user_by_username.get(trainer_username)
            if not client_user or not trainer_user:
                continue

            thread, _ = Thread.objects.get_or_create(client=client_user)

            # Mensaje del cliente si no existe
            if not thread.messages.filter(sender=client_user).exists():
                Message.objects.create(
                    thread=thread,
                    sender=client_user,
                    body=body,
                    is_read_by_admin=False,
                    is_read_by_client=True,
                )
                thread.save()
                msg_count += 1

            # Respuesta del entrenador (algunos hilos)
            replies = TRAINER_REPLIES.get(trainer_username, [])
            if replies and not thread.messages.filter(sender=trainer_user).exists():
                if random.random() > 0.3:  # 70% tienen respuesta
                    reply_body = random.choice(replies)
                    Message.objects.create(
                        thread=thread,
                        sender=trainer_user,
                        body=reply_body,
                        is_read_by_admin=True,
                        is_read_by_client=False,
                    )
                    thread.save()
                    msg_count += 1

        self.stdout.write(f"  + {msg_count} mensajes creados")
