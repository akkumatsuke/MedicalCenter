# ___ Импорт библиотек для работы с GUI ___
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# ___ Импорт файлов проекта ___
# База данных
from DataBase.DataBaseMain import Session, Appointment, AvailableSlot

class AppointmentCard(QWidget):
    def __init__(self, appointment, parent_controller):
        super().__init__()
        self.appointment = appointment
        self.parent_controller = parent_controller
        # Открытие сессии БД
        self.session = Session()
        self.init_ui()

    def init_ui(self):
        doctor = self.appointment.doctor
        spec = doctor.specialty.name if doctor.specialty else "—"

        # Фото врача
        self.photo = QLabel()
        if doctor.photo_path:
            pix = QPixmap(doctor.photo_path)
            if not pix.isNull():
                self.photo.setPixmap(pix.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.photo.setFixedSize(90, 90)

        # Текстовая часть
        self.name_label = QLabel(f"<b>{doctor.name}</b>")
        self.spec_label = QLabel(f"{spec}")
        self.date_label = QLabel(f"Дата: {self.appointment.date.strftime('%d.%m.%Y')}")
        self.time_label = QLabel(f"Время: {self.appointment.time}")

        for l in [self.name_label, self.spec_label, self.date_label, self.time_label]:
            l.setStyleSheet("font-size: 16px; color: #1f2937;")

        # Кнопка отмены
        self.cancel_btn = QPushButton("Отменить запись")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #e04345; }
        """)
        self.cancel_btn.clicked.connect(self.cancel_appointment)

        # Макет текста и кнопки
        text_layout = QVBoxLayout()
        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.spec_label)
        text_layout.addWidget(self.date_label)
        text_layout.addWidget(self.time_label)
        text_layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Основной макет карточки
        layout = QHBoxLayout()
        layout.addWidget(self.photo)
        layout.addLayout(text_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                border: 1px solid #e1e6ef;
                border-radius: 10px;
            }
        """)

    # Отмена записи
    def cancel_appointment(self):
        confirm = self.parent_controller.confirm_cancel_dialog()
        if not confirm:
            return

        slot = AvailableSlot(
            doctor_id=self.appointment.doctor_id,
            date=self.appointment.date,
            time=self.appointment.time
        )
        # Создание слота с отменённой записью
        self.session.add(slot)
        # Удаление записи
        self.session.delete(self.appointment)
        # Сохранение изменений в БД
        self.session.commit()
        # Обновление записей
        self.parent_controller.reload_appointments()