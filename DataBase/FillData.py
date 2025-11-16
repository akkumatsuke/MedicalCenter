# ___ Импорт библиотеки для работы с датой и временем ___
from datetime import datetime, timedelta, date

# ___ Импорт модулей из БД ___
from .DataBaseMain import Base, engine, Session, Position, Specialty, Doctor, Account, Appointment

# Заполнение БД
def fill_data():
    # Открытие сессии БД
    session = Session()
    try:
        # ---------- Должности ----------
        # Проверка существования данных о должностях
        if not session.query(Position).first():
            # Данные должностей
            positions_data = [
                {"id": 1, "name": "Пациент"},
                {"id": 2, "name": "Администратор"},
                {"id": 3, "name": "Доктор"}
            ]
            
            # Сохранение объектов должностей
            positions = [Position(id=p["id"], name=p["name"]) for p in positions_data]
            # Создание должностей в БД
            session.add_all(positions)
            # Сохранение изменений в БД
            session.commit()
            print("Должности добавлены.")

        # Проверка существования данных о специальностях
        if session.query(Specialty).first():
            print("Остальные данные уже существуют, пропуск заполнения.")
            return

        # ---------- Специальности ----------
        # Данные специальностей
        specialties_data = [
            "Педиатр", "Терапевт", "Кардиолог", "Узист", "Хирург",
            "Офтальмолог", "Оториноларинголог", "Стоматолог", "Невролог",
            "Эндокринолог", "Уролог", "Гинеколог", "Дерматолог",
            "Психиатр-нарколог", "Инфекционист", "Рентгенолог",
            "Физиотерапевт", "Забор венозной крови", "Забор капиллярной крови"
        ]

        # Сохранение объектов специальностей
        specialties = [Specialty(name=name) for name in specialties_data]
        # Создание специальностей в БД
        session.add_all(specialties)
        # Сохранение изменений в БД
        session.commit()
        # Словарь быстрого доступа к специальностям по имени
        specialties_map = {s.name: s for s in session.query(Specialty).all()}

        # ---------- Врачи ----------
        # Данные врачей
        doctors_data = [
            {"last_name": "Трошин", "first_name": "Макар", "specialty": "Педиатр", "photo_path": "resources/Doctors/Doctor1M.png", "phone": "+7 (900) 111-22-33"},
            {"last_name": "Воробьев", "first_name": "Артём", "specialty": "Уролог", "photo_path": "resources/Doctors/Doctor2M.png", "phone": "+7 (900) 111-22-34"},
            {"last_name": "Еремеев", "first_name": "Кирилл", "specialty": "Уролог", "photo_path": "resources/Doctors/Doctor3M.png", "phone": "+7 (900) 111-22-35"},
            {"last_name": "Демьянов", "first_name": "Илья", "specialty": "Терапевт", "photo_path": "resources/Doctors/Doctor4M.png", "phone": "+7 (900) 111-22-36"},
            {"last_name": "Комиссаров", "first_name": "Макар", "specialty": "Терапевт", "photo_path": "resources/Doctors/Doctor5M.png", "phone": "+7 (900) 111-22-37"},
            {"last_name": "Сергеев", "first_name": "Иван", "specialty": "Физиотерапевт", "photo_path": "resources/Doctors/Doctor6M.png", "phone": "+7 (900) 111-22-38"},
            {"last_name": "Токарев", "first_name": "Сергей", "specialty": "Рентгенолог", "photo_path": "resources/Doctors/Doctor7M.png", "phone": "+7 (900) 111-22-39"},
            {"last_name": "Злобин", "first_name": "Михаил", "specialty": "Психиатр-нарколог", "photo_path": "resources/Doctors/Doctor8M.png", "phone": "+7 (900) 111-22-40"},
            {"last_name": "Голубев", "first_name": "Фёдор", "specialty": "Психиатр-нарколог", "photo_path": "resources/Doctors/Doctor9M.png", "phone": "+7 (900) 111-22-41"},
            {"last_name": "Иванов", "first_name": "Алексей", "specialty": "Эндокринолог", "photo_path": "resources/Doctors/Doctor10M.png", "phone": "+7 (900) 111-22-42"},
            {"last_name": "Лапшин", "first_name": "Алексей", "specialty": "Невролог", "photo_path": "resources/Doctors/Doctor11M.png", "phone": "+7 (900) 111-22-43"},
            {"last_name": "Киреев", "first_name": "Андрей", "specialty": "Стоматолог", "photo_path": "resources/Doctors/Doctor12M.png", "phone": "+7 (900) 111-22-44"},
            {"last_name": "Шевелев", "first_name": "Лев", "specialty": "Хирург", "photo_path": "resources/Doctors/Doctor13M.png", "phone": "+7 (900) 111-22-45"},
            {"last_name": "Никольский", "first_name": "Максим", "specialty": "Узист", "photo_path": "resources/Doctors/Doctor14M.png", "phone": "+7 (900) 111-22-46"},
            {"last_name": "Богданов", "first_name": "Александр", "specialty": "Кардиолог", "photo_path": "resources/Doctors/Doctor15M.png", "phone": "+7 (900) 111-22-47"},
            {"last_name": "Семенова", "first_name": "Вера", "specialty": "Педиатр", "photo_path": "resources/Doctors/Doctor1W.png", "phone": "+7 (900) 111-22-48"},
            {"last_name": "Корчагина", "first_name": "Варвара", "specialty": "Гинеколог", "photo_path": "resources/Doctors/Doctor2W.png", "phone": "+7 (900) 111-22-49"},
            {"last_name": "Куприянова", "first_name": "Анастасия", "specialty": "Гинеколог", "photo_path": "resources/Doctors/Doctor3W.png", "phone": "+7 (900) 111-22-50"},
            {"last_name": "Тимофеева", "first_name": "Алёна", "specialty": "Дерматолог", "photo_path": "resources/Doctors/Doctor4W.png", "phone": "+7 (900) 111-22-51"},
            {"last_name": "Мартынова", "first_name": "Александра", "specialty": "Терапевт", "photo_path": "resources/Doctors/Doctor5W.png", "phone": "+7 (900) 111-22-52"},
            {"last_name": "Попова", "first_name": "Лидия", "specialty": "Забор капиллярной крови", "photo_path": "resources/Doctors/Doctor6W.png", "phone": "+7 (900) 111-22-53"},
            {"last_name": "Александрова", "first_name": "София", "specialty": "Забор венозной крови", "photo_path": "resources/Doctors/Doctor7W.png", "phone": "+7 (900) 111-22-54"},
            {"last_name": "Олейникова", "first_name": "Варвара", "specialty": "Рентгенолог", "photo_path": "resources/Doctors/Doctor8W.png", "phone": "+7 (900) 111-22-55"},
            {"last_name": "Быкова", "first_name": "Виктория", "specialty": "Инфекционист", "photo_path": "resources/Doctors/Doctor9W.png", "phone": "+7 (900) 111-22-56"},
            {"last_name": "Алексеева", "first_name": "София", "specialty": "Инфекционист", "photo_path": "resources/Doctors/Doctor10W.png", "phone": "+7 (900) 111-22-57"},
            {"last_name": "Блинова", "first_name": "Милана", "specialty": "Эндокринолог", "photo_path": "resources/Doctors/Doctor11W.png", "phone": "+7 (900) 111-22-58"},
            {"last_name": "Малышева", "first_name": "Полина", "specialty": "Эндокринолог", "photo_path": "resources/Doctors/Doctor12W.png", "phone": "+7 (900) 111-22-59"},
            {"last_name": "Виноградова", "first_name": "София", "specialty": "Стоматолог", "photo_path": "resources/Doctors/Doctor13W.png", "phone": "+7 (900) 111-22-60"},
            {"last_name": "Данилова", "first_name": "Виктория", "specialty": "Стоматолог", "photo_path": "resources/Doctors/Doctor14W.png", "phone": "+7 (900) 111-22-61"},
            {"last_name": "Родионова", "first_name": "Виктория", "specialty": "Стоматолог", "photo_path": "resources/Doctors/Doctor15W.png", "phone": "+7 (900) 111-22-62"},
            {"last_name": "Борисова", "first_name": "Мария", "specialty": "Оториноларинголог", "photo_path": "resources/Doctors/Doctor16W.png", "phone": "+7 (900) 111-22-63"},
            {"last_name": "Суворова", "first_name": "Милана", "specialty": "Офтальмолог", "photo_path": "resources/Doctors/Doctor17W.png", "phone": "+7 (900) 111-22-64"},
            {"last_name": "Шувалова", "first_name": "София", "specialty": "Узист", "photo_path": "resources/Doctors/Doctor18W.png", "phone": "+7 (900) 111-22-65"},
            {"last_name": "Королева", "first_name": "Елизавета", "specialty": "Узист", "photo_path": "resources/Doctors/Doctor19W.png", "phone": "+7 (900) 111-22-66"},
            {"last_name": "Филатова", "first_name": "Ева", "specialty": "Кардиолог", "photo_path": "resources/Doctors/Doctor20W.png", "phone": "+7 (900) 111-22-67"}
        ]

        # Сохранение врачей
        doctors = [
            Doctor(
                last_name=d["last_name"],
                first_name=d["first_name"],
                specialty=specialties_map[d["specialty"]],
                photo_path=d["photo_path"],
                phone_number=d["phone"]
            )
            for d in doctors_data
        ]
        # Создание врачей в БД
        session.add_all(doctors)
        # Сохранение изменений в БД
        session.commit()
        print(f"Добавлено {len(doctors)} врачей с номерами телефонов")
        print("Создание аккаунтов для врачей...")
        doctor_accounts_created = 0
        
        # Создание аккаунтов для каждого врача
        for i, doctor in enumerate(doctors, 1):
            # Проверка существования аккаунта с таким номером телефона
            existing_account = session.query(Account).filter_by(phone_number=doctor.phone_number).first()
            if not existing_account:
                # Сохранение нового аккаунта врача
                doctor_account = Account(
                    last_name=doctor.last_name,
                    first_name=doctor.first_name,
                    patronymic_name="",
                    birth_date=date(1980, 1, 1 + (i % 28)),
                    phone_number=doctor.phone_number,
                    snils=f"123-456-789 {i:02d}",
                    password="doctor123",
                    position_id=3
                )
                # Создание аккаунтов врачей в БД
                session.add(doctor_account)
                doctor_accounts_created += 1
        # Сохранение изменений БД
        session.commit()
        print(f"Создано {doctor_accounts_created} аккаунтов для врачей с должностью 'Доктор'")

        # ---------- Администратор ----------
        # Проверка существования аккаунта администратора
        admin_account = session.query(Account).filter_by(phone_number="+7 (111) 111-11-11").first()
        if not admin_account:
            # Сохранение аккаунта администратора
            admin_account = Account(
                last_name="Админов",
                first_name="Админ",
                patronymic_name="Админович",
                birth_date=date(1990, 1, 1),
                phone_number="+7 (111) 111-11-11",
                snils="111-222-333 00",
                password="1",
                position_id=2
            )
            # Добавление администратора в БД
            session.add(admin_account)
            # Сохранение изменений в БД
            session.commit()
            print("Создан аккаунт администратора")

        # ---------- Записи на приём ----------
        # Начальная дата
        start_date = datetime(2025, 11, 10)
        # Конечная дата
        end_date = datetime(2025, 11, 20)
        # Создание списка временных слотов
        time_slots = [f"{h:02d}:{m:02d}" for h in range(9, 18) for m in (0, 30)]
        # Инициализация списка для всех записей
        all_appointments = []
        # Генерация записей для каждого врача
        for doctor in session.query(Doctor).all():
            current_date = start_date
            # Генерация записей для каждого дня в диапазоне дат
            while current_date <= end_date:
                for t in time_slots:
                    all_appointments.append(Appointment(
                        doctor_id=doctor.id,
                        date=current_date.date(),
                        time=t,
                        status='available',
                        account_id=None
                    ))
                current_date += timedelta(days=1)
        # Создание записей в БД
        session.add_all(all_appointments)
        # Сохранение изменений в БД
        session.commit()
        print(f"Добавлено {len(all_appointments)} записей для {len(doctors)} врачей.")
        print("Данные успешно добавлены.")

    # Ошибка при заполнении данных в БД
    except Exception as e:
        # Откат изменений в случае ошибки
        session.rollback()
        print(f"Ошибка при заполнении данных: {e}")
    finally:
        # Закрытие сессии БД
        session.close()

# ---------- Запуск скрипта ----------
if __name__ == "__main__":
    from .DataBaseMain import init_db
    init_db()
    fill_data()
    print("База данных создана и заполнена данными.")
