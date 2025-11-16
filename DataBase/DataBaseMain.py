# ___ Импорт библиотек для работы с SQLAlchemy ___
from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ___ Импорт библиотеки для работы с датой и временем ___
from datetime import datetime, timedelta, date

# Создание движка БД SQLite с именем
engine = create_engine("sqlite:///app.db", echo=False, future=True)

# Создание фабрики сессий для работы с БД
Session = sessionmaker(bind=engine, future=True)

# Создание базового класса для декларативного определения моделей
Base = declarative_base()

# ---------- Таблица должностей ----------
class Position(Base):
    # Инициализация имени сущности в БД
    __tablename__ = "Positions"
    
    # Атрибут кода как первичного ключа
    id = Column(Integer, primary_key=True)
    # Атрибут имени с ограничениями
    name = Column(String(50), unique=True, nullable=False)

    # Строковое представления объекта
    def __repr__(self):
        return f"<Position(name={self.name})>"


# ---------- Таблица аккаунтов ----------
class Account(Base):
    # Инициализация имени сущности в БД
    __tablename__ = "Accounts"
    
    # Атрибут кода как первичного ключа
    id = Column(Integer, primary_key=True)
    # Атрибут фамилии с ограничениями
    last_name = Column(String(50), nullable=False)
    # Атрибут имени с ограничениями
    first_name = Column(String(50), nullable=False)
    # Атрибут отчества с ограничениями
    patronymic_name = Column(String(50), nullable=True)
    # Атрибут даты рождения с ограничениями
    birth_date = Column(Date, nullable=False)
    # Атрибут номера телефона с ограничениями
    phone_number = Column(String(20), unique=True, nullable=False)
    # Атрибут СНИЛС с ограничениями
    snils = Column(String(30), unique=True, nullable=False)
    # Атрибут пароля с ограничениями
    password = Column(String(128), nullable=False)
    # Атрибут с внешним ключом к таблице должностей с ограничениями
    position_id = Column(Integer, ForeignKey("Positions.id"), nullable=False, default=1)
    
    # Отношение один-ко-многим с таблицей записей на приём
    appointments = relationship("Appointment", back_populates="account", cascade="all, delete-orphan")

    # Строковое представления объекта
    def __repr__(self):
        return f"<Account({self.last_name} {self.first_name} {self.patronymic_name}, phone={self.phone_number})>"


# ---------- Таблица специальностей ----------
class Specialty(Base):
    # Инициализация имени сущности в БД
    __tablename__ = "Specialties"
    
    # Атрибут кода как первичного ключа
    id = Column(Integer, primary_key=True)
    # Атрибут названия специальности с ограничениями
    name = Column(String(100), unique=True, nullable=False)
    
    # Отношение один-ко-многим с таблицей врачей с ограничениями
    doctors = relationship("Doctor", back_populates="specialty", cascade="all, delete-orphan")

    # Строковое представления объекта
    def __repr__(self):
        return f"<Specialty(name={self.name})>"


# ---------- Таблица врачей ----------
class Doctor(Base):
    # Инициализация имени сущности в БД
    __tablename__ = "Doctors"
    
    # Атрибут кода как первичного ключа
    id = Column(Integer, primary_key=True)
    # Атрибут фамилии с ограничениями
    last_name = Column(String(50), nullable=False)
    # Атрибут имени с ограничениями
    first_name = Column(String(50), nullable=False)
    # Атрибут с внешним ключом к таблице специальностей с ограничениями
    specialty_id = Column(Integer, ForeignKey("Specialties.id"), nullable=True)
    # Атрибут пути к фотографии с ограничениями
    photo_path = Column(String(255), nullable=True)
    # Атрибут номера телефона с ограничениями
    phone_number = Column(String(20), unique=True, nullable=True)    
    # Атрибут статуса активности врача
    is_active = Column(Integer, default=1)
    
    # Отношение многие-к-одному с таблицей специальностей
    specialty = relationship("Specialty", back_populates="doctors")
    # Отношение один-ко-многим с таблицей записей с ограничениями
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")

    # Строковое представления объекта
    def __repr__(self):
        return f"<Doctor({self.last_name} {self.first_name}, specialty={self.specialty.name})>"


# ---------- Таблица записей на приём ----------
class Appointment(Base):
    # Инициализация имени сущности в БД
    __tablename__ = "Appointments"
    
    # Атрибут кода как первичного ключа
    id = Column(Integer, primary_key=True)
    # Атрибут внешнего ключа к таблицк аккаунтов с ограничениями
    account_id = Column(Integer, ForeignKey("Accounts.id"), nullable=True)
    # Атрибут внешнего ключа к таблице врачей с ограничениями
    doctor_id = Column(Integer, ForeignKey("Doctors.id"), nullable=False)
    # Атрибут даты с ограничениями
    date = Column(Date, nullable=False)
    # Атрибут времени с ограничениями
    time = Column(String(10), nullable=False)
    # Атрибут статуса записи с ограничениями
    status = Column(String(20), nullable=False, default='available')  # 'available' или 'booked'
    
    # Отношение многие-к-одному с таблицей аккаунтов
    account = relationship("Account", back_populates="appointments")
    # Отношение многие-к-одному с таблицей врачей
    doctor = relationship("Doctor", back_populates="appointments")

    # Строковое представления объекта
    def __repr__(self):
        return f"<Appointment(patient={self.account_id}, doctor_id={self.doctor_id}, date={self.date}, time={self.time}, status={self.status})>"


# Инициализация БД
def init_db():
    # Создание всех таблиц в БД
    Base.metadata.create_all(engine)
