# ___ Импорт библиотек для работы с системой ___
import sys
import os

# ___ Импорт библиотеки для работы с датой и временем ___
from datetime import date, datetime

# ___ Импорт библиотек для работы с GUI ___
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QLabel, QPushButton, QHBoxLayout,
                             QVBoxLayout, QWidget, QGridLayout, QScrollArea, QGraphicsDropShadowEffect,
                             QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QTabWidget, QLineEdit, QMessageBox, QComboBox)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

# Получение абсолютного путя к файлу
def get_resource_path(relative_path):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_path, relative_path)
        print(f"Поиск файла: {full_path}")
        if os.path.exists(full_path):
            print(f"Файл найден: {full_path}")
            return full_path.replace('\\', '/')
        else:
            print(f"Файл не найден: {full_path}")
            return ""
    except Exception as e:
        print(f"Ошибка получения пути: {e}")
        return ""

# ___ Импорт файлов проекта ___
# Запоминание врача и пользователя
from CurrentUser import get_current_doctor, set_current_doctor, set_current_user, get_current_user, clear_current_user
# База данных
from DataBase.DataBaseMain import Session, Account, init_db, Specialty, Doctor, Appointment
# Данные для БД
from DataBase.FillData import fill_data
# Окна
from Windows.AuthorizationWindow.AuthorizationWindowUi import Ui_AuthorizationWindowUi
from Windows.RegistrationWindow.RegistrationWindowUi import Ui_RegistrationWindow
from Windows.ErrorGosWindow.ErrorWindowUi import Ui_ErrorGosWindow
from Windows.AllHomePages.AllHomePagesUi import Ui_HomeWindow
from Windows.ForgotPasswordWindow.ForgotPasswordWindowUi import Ui_ForgotPasswordWindow
from Windows.DoctorWindow.DoctorWindowUi import Ui_DoctorWindow
from Windows.AddDoctorDialog.AddDoctorDialogUi import Ui_AddDoctorDialog
from Windows.AddSlotDialog.AddSlotDialogUi import Ui_AddSlotDialog
from Windows.EditDoctorDialog.EditDoctorDialog import Ui_EditDoctorDialog


# ---------- Общие классы ----------
# Форматирование номера телефона
class PhoneFormatter:
    # Автовставка символов
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def format_phone_text(text):
        prefix = "+7 ("
        # Фильтрация текста (только цифры, объединённые в одну строку)
        digits = ''.join(filter(str.isdigit, text))
        # Убирает цифру, если номер начинается с 7
        if digits.startswith("7"): digits = digits[1:]
        result = prefix
        if len(digits) > 0: result += digits[0:3]
        if len(digits) >= 4: result += ") " + digits[3:6]
        if len(digits) >= 7: result += "-" + digits[6:8]
        if len(digits) >= 9: result += "-" + digits[8:10]
        return result

    # Позиционирование курсора при вводе и форматирование в реальном времени
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def on_phone_text_changed(line_edit, text):
        # Форматирование введенного текста
        formatted_text = PhoneFormatter.format_phone_text(text)
        # Получение текущей позиции курсора в поле ввода
        cursor_pos = line_edit.cursorPosition()
        # Перемещение курсора, если он находится в зоне префикса
        if cursor_pos < len("+7 ("): cursor_pos = len("+7 (")
        # Разницы длины между отформатированным и текущим текстом
        delta = len(formatted_text) - len(line_edit.text())
        # Расчет новой позиции курсора с учетом изменения длины текста
        new_cursor_pos = cursor_pos + max(0, delta)
        line_edit.blockSignals(True)
        # Установка отформатированного текста в поле ввода
        line_edit.setText(formatted_text)
        line_edit.blockSignals(False)
        # Установка курсора в новую позицию
        line_edit.setCursorPosition(min(new_cursor_pos, len(formatted_text)))

# Форматирование СНИЛСА
class SNILSFormatter:
    # Автовставка символов
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def format_snils_text(text):
        # Фильтрация текста (только цифры, объединённые в одну строку)
        digits = ''.join(filter(str.isdigit, text))
        result = ""
        if len(digits) >= 1: result += digits[0:3]
        if len(digits) >= 4: result += "-" + digits[3:6]
        if len(digits) >= 7: result += "-" + digits[6:9]
        if len(digits) >= 10: result += " " + digits[9:11]
        return result

    # Форматирование в реальном времени
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def on_snils_text_changed(line_edit, text):
        # Форматирование введенного текста
        formatted_text = SNILSFormatter.format_snils_text(text)
        line_edit.blockSignals(True)
        # Установка отформатированного текста в поле ввода
        line_edit.setText(formatted_text)
        line_edit.blockSignals(False)

# Форматирование даты рождения
class DateFormatter:
    # Автовставка символов
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def format_birth_text(text):
        # Фильтрация текста (только цифры, объединённые в одну строку)
        digits = ''.join(filter(str.isdigit, text))
        result = ""
        if len(digits) >= 1: result += digits[0:2]
        if len(digits) >= 3: result += "." + digits[2:4]
        if len(digits) >= 5: result += "." + digits[4:8]
        return result

    # Форматирование в реальном времени
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def on_birth_text_changed(line_edit, text):
        # Форматирование введенного текста
        formatted_text = DateFormatter.format_birth_text(text)
        line_edit.blockSignals(True)
        # Установка отформатированного текста в поле ввода
        line_edit.setText(formatted_text)
        line_edit.blockSignals(False)

# Управление окнами
class WindowManager:
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def open_window(current_window, new_window_class, close_current=True):
        new_window = new_window_class()
        new_window.show()
        if close_current:
            current_window.close()

# Загрзка SVG фотографий
class SVGLoader:
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def load_svg_to_widget(svg_path, parent_widget, x=0, y=0):
        # Создание SVG виджета с путём к файлу и родительским виджетом
        svg_widget = QSvgWidget(svg_path, parent=parent_widget)
        # Установка фиксированного размера равного размеру родительского
        svg_widget.setFixedSize(parent_widget.size())
        svg_widget.move(x, y)
        svg_widget.show()
        return svg_widget

# Установка стилей комбо-боксов
class StyleManager:
    # Не требует доступа к экземпляру или классу
    @staticmethod
    def get_combo_box_style():
        arrow_path = get_resource_path("resources/arrow-down.svg")
        # Изображение стрелки, если путь найден
        arrow_image = f"image: url('{arrow_path}');" if arrow_path else ""
        return f"""
                /* Основной стиль QComboBox */
                QComboBox {{
                    background-color: rgba(0,0,0,0);
                    border: 1px solid #B4B4B4;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-size: 15px;
                    font-weight: bold;
                    color: #2a3b47;
                    font-family: "Segoe UI", "Arial";
                }}

                /* Стиль при наведении курсора */
                QComboBox:hover {{
                    border: 1px solid #5fa8d3;
                }}

                /* Стиль при фокусе */
                QComboBox:focus {{
                    border: 1px solid #3498db;
                    background-color: #f7fbff;
                }}

                /* Стиль выпадающей стрелки */
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 28px;
                    border-left: 1px solid #c5d8e6;
                    background-color: #f0f6fa;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }}

                /* Стиль стрелки списка */
                QComboBox::down-arrow {{
                    {arrow_image}
                    width: 12px;
                    height: 12px;
                }}

                /* Стиль при открытом комбо-боксе */
                QComboBox:on {{
                    background-color: #f7fbff;
                }}

                /* Стиль списка элементов */
                QComboBox QAbstractItemView {{
                    background-color: #ffffff;
                    border: 1px solid #c5d8e6;
                    border-radius: 8px;
                    outline: none;
                    selection-background-color: #5fa8d3;
                    selection-color: #ffffff;
                    font-size: 15px;
                    font-family: "Segoe UI", "Arial";
                }}

                /* Стиль отдельных элементов */
                QComboBox QAbstractItemView::item {{
                    height: 28px;
                    padding: 4px 8px;
                }}

                /* Стиль полосы прокрутки */
                QScrollBar:vertical {{
                    border: none;
                    background: #f2f5f8;
                    width: 8px;
                    margin: 4px;
                    border-radius: 4px;
                }}

                /* Стиль ползунка */
                QScrollBar::handle:vertical {{
                    background: #b6c9d6;
                    border-radius: 4px;
                }}

                /* Стиль ползунка при наведении курсора */
                QScrollBar::handle:vertical:hover {{
                    background: #9fbcd1;
                }}
            """

# ---------- Кастомное окно сообщений ----------
class CustomMessage(QDialog):
    # Принимает заголовок и текст сообщения
    def __init__(self, title: str, text: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: white; color: black;")
        self.setFixedSize(300, 150)
        # Вертикальный компоновщик
        layout = QVBoxLayout()
        # Переданный текст
        label = QLabel(text)
        label.setStyleSheet("color: black; font-size: 14px;")
        label.setWordWrap(True)
        layout.addWidget(label)
        btn = QPushButton("Ок")
        btn.setStyleSheet("background-color: #f0f0f0; color: black; min-width: 80px; min-height: 30px;")
        
        # Регистрация нажатия кнопок
        btn.clicked.connect(self.accept)
        
        # Добавление кнопки
        layout.addWidget(btn)
        # Установка компоновщика
        self.setLayout(layout)
        
        # Запуск
        self.exec()

# ---------- Окно Авторизации ----------
class AuthorizationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 640)
        self.ui = Ui_AuthorizationWindowUi()
        self.ui.setupUi(self)
        
        # Фотографии
        self.ui.BackgroundImg.setPixmap(QPixmap("resources/backgroundImg.jpg"))
        self.ui.BackgroundImg.setScaledContents(True)
        
        # Маски полей
        self.ui.LoginBox.setPlaceholderText("Номер телефона")
        self.ui.PasswordBox.setEchoMode(self.ui.PasswordBox.EchoMode.Password)
        
        # Форматирование полей
        self.ui.LoginBox.textChanged.connect(lambda text: PhoneFormatter.on_phone_text_changed(self.ui.LoginBox, text))
        
        # Регистрации нажатия кнопок
        self.ui.SignUpBtn.clicked.connect(self.Open_Registration_Window)
        self.ui.SignUpBtn.clicked.connect(self.close)
        self.ui.LogInGosBtn.clicked.connect(self.Open_Error_Gos_Window)
        self.ui.LogInGosBtn.clicked.connect(self.close)
        self.ui.LogInBtn.clicked.connect(self.Login_User)
        self.ui.ForgotPassBtn.clicked.connect(self.Open_Forgot_Password_Window)
        self.ui.ForgotPassBtn.clicked.connect(self.close)
        
        # Кнопка показа/скрытия пароля
        self.password_visible = False
        self.toggle_password_btn = QPushButton(parent=self.ui.PasswordBox)
        self.toggle_password_btn.setGeometry(250, 10, 40, 30)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2A8BD9;
            }
        """)
        self.toggle_password_btn.setText("🔒")
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

    # Переключение видимости пароля
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.ui.PasswordBox.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("👁")
        else:
            self.ui.PasswordBox.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("🔒")

    # Авторизация пользователя
    def Login_User(self):
        # Получение и очистка данных из полей
        phone = self.ui.LoginBox.text().strip()
        password = self.ui.PasswordBox.text().strip()
        
        if not all([phone, password]):
            CustomMessage("Ошибка", "Введите номер телефона и пароль")
            return
        
        # Извлечение только цифр
        digits_phone = ''.join(filter(str.isdigit, phone))
        if len(digits_phone) != 11:
            CustomMessage("Ошибка", "Введите полный номер телефона")
            return
        
        # Открытие сессии БД
        session = Session()
        # Поиск аккаунта в БД по логину и паролю
        user = session.query(Account).filter_by(phone_number=phone, password=password).first()
        
        if user:
            set_current_user(user.id)
            fio = f"{user.last_name} {user.first_name} {user.patronymic_name}"
            
            # Проверка должности аккаунта
            # Администратор
            if user.position_id == 2:
                CustomMessage("Успех", f"Добро пожаловать, Администратор {fio}!")
                self.Open_Admin_Window()
            # Врач
            elif user.position_id == 3:
                # Проверка наличия врача в БД
                doctor = session.query(Doctor).filter_by(phone_number=phone).first()
                if doctor:
                    set_current_doctor(doctor.id)
                    CustomMessage("Успех", f"Добро пожаловать, Доктор {fio}!")
                    self.Open_Doctor_Window()
                else:
                    CustomMessage("Ошибка", "Профиль доктора не найден")
            # Пациент
            elif user.position_id == 1:
                CustomMessage("Успех", f"Добро пожаловать, {fio}!")
                self.Open_Home_Window()
                self.close()
            else:
                CustomMessage("Ошибка", "Неизвестная должность")
        else:
            CustomMessage("Ошибка", "Неверный телефон или пароль")
        
        # Закрытие сессии БД
        session.close()

    # Открытие главного окна
    def Open_Home_Window(self):
        self.home_window = HomeWindow()
        self.home_window.show()

    # Открытие окна администратора
    def Open_Admin_Window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
    
    # Открытие окна врача
    def Open_Doctor_Window(self):
        self.doctor_window = DoctorWindow()
        self.doctor_window.show()

    # Открытие окна ошибки при входе через госуслуги
    def Open_Error_Gos_Window(self):
        self.error_window = ErrorGosWindow()
        self.error_window.show()
    
    # Открытие окна регистрации
    def Open_Registration_Window(self):
        self.signup_window = RegistrationWindow()
        self.signup_window.show()
    
    # Открытие окна восстановления пароля
    def Open_Forgot_Password_Window(self):
        self.forgot_password_window = ForgotPasswordWindow()
        self.forgot_password_window.show()

# ---------- Окно регистрации ----------
class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 640)
        self.ui = Ui_RegistrationWindow()
        self.ui.setupUi(self)
        
        # Фотографии
        self.ui.BackgroundImg.setPixmap(QPixmap("resources/backgroundImg.jpg"))
        self.ui.BackgroundImg.setScaledContents(True)
        SVGLoader.load_svg_to_widget("resources/backArrow.svg", self.ui.BackBtn)
        
        # Маски полей
        self.ui.FIOBox.setPlaceholderText("ФИО")
        self.ui.PasswordBox.setPlaceholderText("Пароль")
        self.ui.PasswordBox.setEchoMode(self.ui.PasswordBox.EchoMode.PasswordEchoOnEdit)
        self.ui.PhoneNumberBox.setPlaceholderText("Номер телефона")
        self.ui.SNILSBox.setPlaceholderText("СНИЛС")
        self.ui.BirthdateBox.setPlaceholderText("Дата рождения (дд.мм.гггг)")
        
        # Форматирование полей
        self.ui.PhoneNumberBox.textChanged.connect(lambda text: PhoneFormatter.on_phone_text_changed(self.ui.PhoneNumberBox, text))
        self.ui.SNILSBox.textChanged.connect(lambda text: SNILSFormatter.on_snils_text_changed(self.ui.SNILSBox, text))
        self.ui.BirthdateBox.textChanged.connect(lambda text: DateFormatter.on_birth_text_changed(self.ui.BirthdateBox, text))
        
        # Регистрация нажатия кнопок
        self.ui.BackBtn.clicked.connect(self.Open_Authorization_Window)
        self.ui.SignUpBtn.clicked.connect(self.Register_User)
        
        # Кнопка показа/скрытия пароля
        self.password_visible = False
        self.toggle_password_btn = QPushButton(parent=self.ui.PasswordBox)
        self.toggle_password_btn.setGeometry(250, 10, 40, 30)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2A8BD9;
            }
        """)
        self.toggle_password_btn.setText("🔒")
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

    # Переключение видимости пароля
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.ui.PasswordBox.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("👁")
        else:
            self.ui.PasswordBox.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("🔒")

    # Регистрация аккаунта
    def Register_User(self):
        # Получение и очистка данных из полей
        fio_text = self.ui.FIOBox.text().strip()
        birth_text = self.ui.BirthdateBox.text().strip()
        phone = self.ui.PhoneNumberBox.text().strip()
        snils = self.ui.SNILSBox.text().strip()
        password = self.ui.PasswordBox.text().strip()

        # Проверка вверно введённого ФИО
        # Разделение ФИО на части
        parts = fio_text.split()
        if len(parts) != 3:
            CustomMessage("Ошибка", "Неверно введено ФИО")
            return
        # Сохранение ФИО по частям
        last_name, first_name, patronymic_name = parts

        if not all([birth_text, phone, snils, password]):
            CustomMessage("Ошибка", "Заполните все поля.")
            return
        
        if len(password) < 8:
            CustomMessage("Ошибка", "Пароль должен содержать не менее 8 символов")
            return
        
        # Проверка даты рождения
        try:
            # Преобразование текста в дату
            birth_date = datetime.strptime(birth_text, "%d.%m.%Y").date()
        except ValueError:
            CustomMessage("Ошибка", "Некорректная дата рождения")
            return
        
        # Сохранение текущей даты
        today = date.today()
        
        # Сохранение возраста пользователя
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 14:
            CustomMessage("Ошибка", "Возраст должен быть не менее 14 лет")
            return
        elif age > 100:
            CustomMessage("Ошибка", "Возраст должен быть не более 100 лет")
            return
        
        # Извлечение только цифр
        digits_phone = ''.join(filter(str.isdigit, phone))
        if len(digits_phone) != 11:
            CustomMessage("Ошибка", "Введите полный номер телефона")
            return
        
        # Извлечение только цифр
        digits_snils = ''.join(filter(str.isdigit, snils))
        if len(digits_snils) != 11:
            CustomMessage("Ошибка", "Введите полный СНИЛС")
            return
        
        if not (self.ui.DataCheck.isChecked() and self.ui.ConfCheck.isChecked()):
            CustomMessage("Ошибка", "Необходимы согласия")
            return
        
        # Открытие сессии БД
        session = Session()
        
        if session.query(Account).filter_by(phone_number=phone).first():
            CustomMessage("Ошибка", "Такой номер телефона уже зарегистрирован")
            # Закрытие сессии БД
            session.close()
            return
        if session.query(Account).filter_by(snils=snils).first():
            CustomMessage("Ошибка", "Такой СНИЛС уже зарегистрирован")
            # Закрытие сессии БД
            session.close()
            return
            
        # Сохранение должности по умолчанию
        user_position_id = 1

        # Сохранение нового аккаунта
        new_user = Account(
            last_name=last_name,
            first_name=first_name,
            patronymic_name=patronymic_name,
            birth_date=birth_date,
            phone_number=phone,
            snils=snils,
            password=password,
            position_id=user_position_id
        )
        
        # Создание нового акккаунта
        session.add(new_user)
        # Сохранение изменений в БД
        session.commit()
        # Закрытие сессии БД
        session.close()
        CustomMessage("Успех", "Регистрация прошла успешно!")
        self.Open_Authorization_Window()
        self.close()

    # Открытие окна авторизации
    def Open_Authorization_Window(self):
        self.authorization_window = AuthorizationWindow()
        self.authorization_window.show()
        self.close()


# ---------- Окно ошибки входа через госуслуги ----------
class ErrorGosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 640)
        self.ui = Ui_ErrorGosWindow()
        self.ui.setupUi(self)

        # Фотографии
        SVGLoader.load_svg_to_widget("resources/error.svg", self.ui.ErrorImg)
        self.ui.BackgroundImg.setPixmap(QPixmap("resources/backgroundImg.jpg"))
        self.ui.BackgroundImg.setScaledContents(True)

        # Регистрация нажатия кнопок
        self.ui.CloseBtn.clicked.connect(self.Open_Authorization_Window)

    # Открытие окна авторизации
    def Open_Authorization_Window(self):
        self.authorization_window = AuthorizationWindow()
        self.authorization_window.show()
        self.close()

# ---------- Окна восстановления пароля ----------
class ForgotPasswordWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 640)
        self.ui = Ui_ForgotPasswordWindow()
        self.ui.setupUi(self)
        
        # Фотографии
        self.ui.LogoImg.setPixmap(QPixmap("resources/logo.png"))
        self.ui.LogoImg.setScaledContents(True)
        self.ui.BackgroundImg.setPixmap(QPixmap("resources/backgroundImg.jpg"))
        self.ui.BackgroundImg.setScaledContents(True)
        
        # Маска поля
        self.ui.LoginBox.setPlaceholderText("Номер телефона")
        
        # Форматирование полей
        self.ui.LoginBox.textChanged.connect(lambda text: PhoneFormatter.on_phone_text_changed(self.ui.LoginBox, text))

        # Регистрация нажатия кнопок
        self.ui.BackBtn.clicked.connect(self.open_auth_window)
        self.ui.GivePassBtn.clicked.connect(self.recover_password)

    # Восстановление пароля
    def recover_password(self):
        # Получение и очистка данных из полей
        phone = self.ui.LoginBox.text().strip()
        # Извлечение только цифр
        digits_phone = ''.join(filter(str.isdigit, phone))

        if len(digits_phone) != 11:
            CustomMessage("Ошибка", "Введите полный номер телефона")
            return

        # Открытие сессии БД
        session = Session()
        # Поиск аккаунта в БД
        user = session.query(Account).filter_by(phone_number=phone).first()
        # Закрытие сессии БД
        session.close()

        if user:
            CustomMessage("Ваш пароль", f"Ваш пароль: {user.password}")
        else:
            CustomMessage("Ошибка", "Пользователь с таким номером не найден")
    
    # Открытие окна авторизации
    def open_auth_window(self):
        self.authorization_window = AuthorizationWindow()
        self.authorization_window.show()
        self.close()


# ---------- Главное окно ----------
class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 640)
        self.ui = Ui_HomeWindow()
        self.ui.setupUi(self)

        # Фотографии
        self.ui.LogoImg.setPixmap(QPixmap("resources/logo.png"))
        self.ui.LogoImg.setScaledContents(True)
        self.ui.GlavVrachImg.setPixmap(QPixmap("resources/glavVrach.png"))
        self.ui.GlavVrachImg.setScaledContents(True)
        self.add_svg_icons()
        self.ui.BackgroundImg.setPixmap(QPixmap("resources/backgroundImg.jpg"))
        self.ui.BackgroundImg.setScaledContents(True)

        # Регистрация нажатия кнопок
        self.ui.MyAccountBtn.clicked.connect(self.open_my_account_page)
        self.ui.BackBtn.clicked.connect(self.open_home_page)
        self.ui.MakeRecordBtn.clicked.connect(self.open_make_record_page)
        self.ui.MyRecordsBtn.clicked.connect(self.open_my_records_page)

        # Инициализация контроллеров страниц
        self.home_controller = HomePageController(self.ui, self)
        self.make_record_controller = MakeRecordPageController(self.ui, self)
        self.my_account_controller = MyAccountPageController(self.ui, self)
        self.my_records_controller = MyRecordsPageController(self.ui, self)

        # Устновка начальной страницы
        self.ui.stackedWidget.setCurrentWidget(self.ui.HomePage)

    # Загрузка SVG фотографий
    def add_svg_icons(self):
        SVGLoader.load_svg_to_widget("resources/maps.svg", self.ui.MapsImg, 24, 12)
        SVGLoader.load_svg_to_widget("resources/mail.svg", self.ui.MailImg, 23, 20)
        SVGLoader.load_svg_to_widget("resources/phone.svg", self.ui.PhoneImg, 23, 7)
        SVGLoader.load_svg_to_widget("resources/backArrow.svg", self.ui.BackBtn)

    # Установка страницы аккаунта
    def open_my_account_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.MyAccountPage)

    # Установка главной страницы
    def open_home_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.HomePage)
    
    # Устновка страницы создания записи
    def open_make_record_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.MakeRecordPage)
    
    # Установка страницы записей
    def open_my_records_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.MyRecordsPage)
        # Обновление списка записей
        self.my_records_controller.reload_appointments()
    
    # Очистка текущего пользователя
    def logout(self):
        clear_current_user()
    
    # Открытие окна авторизации
    def open_auth_window(self):
        self.authorization_window = AuthorizationWindow()
        self.authorization_window.show()
        self.close()


# ---------- Контроллеры страниц главного окна ----------
class HomePageController:
    def __init__(self, ui, parent_window: HomeWindow):
        self.ui = ui
        self.parent = parent_window

# ---------- Контроллер страницы аккаунта ----------
class MyAccountPageController:
    def __init__(self, ui, parent_window: HomeWindow):
        self.ui = ui
        self.parent = parent_window
        # Открытие сессии БД
        self.session = Session()

        # Загрузка данных аккаунта
        self.load_user_data()

        # Регистрация нажатия кнопок
        self.ui.BackBtn.clicked.connect(self.parent.open_home_page)
        self.ui.LogOutBtn.clicked.connect(self.parent.logout)
        self.ui.LogOutBtn.clicked.connect(self.parent.open_auth_window)
        self.ui.ChangePasswordBtn.clicked.connect(self.change_password)

    # Загрузка данных аккаунта
    def load_user_data(self):
        user_id = get_current_user()
        if not user_id:
            return
        
        # Получение аккаунта в БД
        user = self.session.get(Account, user_id)
        
        # Вывод данных аккаунта в поля
        if user:
            fio = f"{user.last_name} {user.first_name} {user.patronymic_name}"
            
            # Установка данных в поля
            self.ui.FIOText.setText(fio)
            self.ui.PhoneNumberText.setText(user.phone_number)
            self.ui.SNILSText.setText(user.snils)
            self.ui.BirthdayText.setText(user.birth_date.strftime("%d.%m.%Y"))
    
    # Изменение пароля аккаунта
    def change_password(self):
        user_id = get_current_user()
        
        if not user_id:
            CustomMessage("Ошибка", "Не удалось определить пользователя")
            return
        
        # Получение аккаунта в БД
        user = self.session.get(Account, user_id)
        
        if not user:
            CustomMessage("Ошибка", "Пользователь не найден")
            return

        # Получение и очистка данных из полей
        new_password = self.ui.PasswordBox.text().strip()
        confirm_password = self.ui.PasswordBox_2.text().strip()

        if not new_password or not confirm_password:
            CustomMessage("Ошибка", "Заполните все поля пароля")
            return

        if new_password != confirm_password:
            CustomMessage("Ошибка", "Пароли не совпадают")
            return

        if len(new_password) < 8:
            CustomMessage("Ошибка", "Пароль должен содержать минимум 8 символа")
            return

        if new_password == user.password:
            CustomMessage("Ошибка", "Новый пароль должен отличаться от предыдущего")
            return

        try:
            user.password = new_password
            # Сохранение изменений в БД
            self.session.commit()
            # Очистка полей
            self.ui.PasswordBox.clear()
            self.ui.PasswordBox_2.clear()
            CustomMessage("Успех", "Пароль успешно изменен")
        except Exception as e:
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при изменении пароля: {str(e)}")

# ---------- Контроллер страницы создания записи ----------
class MakeRecordPageController:
    def __init__(self, ui, parent_window: HomeWindow):
        self.ui = ui
        self.parent = parent_window
        # Создание сессии БД
        self.session = Session()
        # Инициализация текущего врача
        self.current_doctor_id = None

        # Стили комбо-боксов
        self.apply_combo_styles()

        # Обработка изменения данных в комбо-боксах
        self.ui.DoctorSpecComboBox.currentIndexChanged.connect(self.on_specialty_changed)
        self.ui.DoctorFIOComboBox.currentIndexChanged.connect(self.on_doctor_changed)
        self.ui.RecordDateComboBox.currentIndexChanged.connect(self.on_date_changed)
        
        # Регистрация нажатия кнопок
        self.ui.CreateBtn.clicked.connect(self.on_create_appointment)
        self.ui.BackBtnMakeRecord.clicked.connect(self.parent.open_home_page)
        
        # Фотографии
        self.ui.LogoImgMakeRecord.setPixmap(QPixmap("resources/logo.png"))
        self.ui.LogoImgMakeRecord.setScaledContents(True)
        SVGLoader.load_svg_to_widget("resources/passport.svg", self.ui.PassportImg, 24, 11)
        SVGLoader.load_svg_to_widget("resources/clock.svg", self.ui.ClockImg, 20, 10)
        SVGLoader.load_svg_to_widget("resources/backArrow.svg", self.ui.BackBtnMakeRecord, 3, 8)

        # Загрузка специальностей
        self.load_specialties()

    # Стили комбо-боксов
    def apply_combo_styles(self):
        combos = [
            self.ui.DoctorSpecComboBox,
            self.ui.DoctorFIOComboBox, 
            self.ui.RecordDateComboBox,
            self.ui.RecordTimeComboBox
        ]
        
        # Применение стилей к каждому комбо-боксу
        for combo in combos:
            combo.setStyleSheet(StyleManager.get_combo_box_style())

    # Загрузка специальностей
    def load_specialties(self):
        try:
            self.ui.DoctorSpecComboBox.blockSignals(True)
            self.ui.DoctorSpecComboBox.clear()
            
            self.ui.DoctorSpecComboBox.addItem("Выберите специальность", None)
            
            # Получение специальностей из БД
            specs = self.session.query(Specialty).order_by(Specialty.name).all()
            print(f"Найдено специальностей: {len(specs)}")
            
            # Добавление специальностей в комбо-бокс
            for s in specs:
                self.ui.DoctorSpecComboBox.addItem(s.name, s.id)
            
            self.ui.DoctorSpecComboBox.blockSignals(False)
        except Exception as e:
            print(f"Ошибка загрузки специальностей: {e}")
            self.ui.DoctorSpecComboBox.blockSignals(False)

    # Изменение специальности в комбо-боксе
    def on_specialty_changed(self, index):
        # Получение кода выбранной специальности
        spec_id = self.ui.DoctorSpecComboBox.currentData()
        
        # Очистка комбо-боксов
        self.ui.DoctorFIOComboBox.clear()
        self.ui.RecordDateComboBox.clear()
        self.ui.RecordTimeComboBox.clear()
        
        if not spec_id:
            return
            
        try:
            # Получение врачей выбранной специальности из БД
            doctors = self.session.query(Doctor).filter_by(specialty_id=spec_id).order_by(Doctor.last_name).all()
            print(f"Найдено врачей для специальности {spec_id}: {len(doctors)}")
            
            self.ui.DoctorFIOComboBox.addItem("Выберите врача", None)
            
            # Добавление каждого врача в комбо-бокс
            for d in doctors:
                fio = f"{d.last_name} {d.first_name}"
                self.ui.DoctorFIOComboBox.addItem(fio, d.id)
        except Exception as e:
            print(f"Ошибка загрузки врачей: {e}")

    # Изменение врача в комбо-боксе
    def on_doctor_changed(self, index):
        # Получение кода выбранного врача
        doc_id = self.ui.DoctorFIOComboBox.currentData()
        # Сохранение кода текущего врача
        self.current_doctor_id = doc_id
        
        # Очистка комбо-боксов
        self.ui.RecordDateComboBox.clear()
        self.ui.RecordTimeComboBox.clear()

        # Очистка информации о враче
        if not doc_id:
            self.clear_doctor_info()
            return

        try:
            # Получение врача из БД
            doctor = self.session.get(Doctor, doc_id)
            # Выгрузка информации о враче
            if doctor:
                # Выгрузка фотографии врача если путь указан
                if doctor.photo_path and os.path.exists(doctor.photo_path):
                    pix = QPixmap(doctor.photo_path)
                    if not pix.isNull():
                        self.ui.DoctorImg.setPixmap(pix)
                        self.ui.DoctorImg.setScaledContents(True)
                    else:
                        # Установка заглушки если фото не загружено
                        self.ui.DoctorImg.clear()
                else:
                    # Установка заглушки если путь не указан
                    self.ui.DoctorImg.clear()
                    
                # Установка ФИО врача
                fio = f"{doctor.last_name} {doctor.first_name}"
                self.ui.DoctorFIOText.setText(fio)
                # Установка специальности врача
                self.ui.DoctorSpecText.setText(doctor.specialty.name if doctor.specialty else "")
            else:
                # Очистка информации о враче
                self.clear_doctor_info()

            # Загрузка свободных слотов для выбранного врача
            self.load_dates_for_doctor()
        except Exception as e:
            print(f"Ошибка загрузки информации о враче: {e}")
            self.clear_doctor_info()

    # Очистка информации о враче
    def clear_doctor_info(self):
        self.ui.DoctorImg.clear()
        self.ui.DoctorFIOText.setText("")
        self.ui.DoctorSpecText.setText("")

    # Загрузка свободных слотов для выбранного врача
    def load_dates_for_doctor(self):
        # Очистка комбо-боксов
        self.ui.RecordDateComboBox.clear()
        if not self.current_doctor_id:
            return
        
        try:
            # Получение дат для доступных записей врача
            rows = (self.session.query(Appointment.date)
                    .filter(Appointment.doctor_id == self.current_doctor_id,
                            Appointment.status == 'available',
                            Appointment.date >= date.today())
                    .distinct()
                    .order_by(Appointment.date)
                    .all())
            
            print(f"Найдено дат для врача {self.current_doctor_id}: {len(rows)}")
            
            self.ui.RecordDateComboBox.addItem("Выберите дату", None)
            
            # Добавление каждой даты в комбо-бокс
            for r in rows:
                pydate = r[0]
                formatted = pydate.strftime("%d.%m.%Y")
                self.ui.RecordDateComboBox.addItem(formatted, pydate)
        except Exception as e:
            print(f"Ошибка загрузки дат: {e}")

    # Изменение даты в комбо-боксе
    def on_date_changed(self, index):
        # Очистка комбо-боксов
        self.ui.RecordTimeComboBox.clear()
        
        # Проверка индекса и наличия выбранного врача
        if index < 0 or not self.current_doctor_id:
            return
        
        # Получение выбранной даты
        pydate = self.ui.RecordDateComboBox.currentData()
        
        if not pydate:
            return
        
        try:
            # Получение доступных записей времени для врача и даты
            appointments = (self.session.query(Appointment)
                     .filter(Appointment.doctor_id == self.current_doctor_id,
                             Appointment.date == pydate,
                             Appointment.status == 'available')
                     .order_by(Appointment.time)
                     .all())
            
            print(f"Найдено доступных записей для даты {pydate}: {len(appointments)}")
            
            if not appointments:
                self.ui.RecordTimeComboBox.addItem("Нет доступного времени")
                return
            
            self.ui.RecordTimeComboBox.addItem("Выберите время", None)
            
            # Добавление каждого слота времени в комбо-бокс
            for app in appointments:
                self.ui.RecordTimeComboBox.addItem(app.time, app.id)
        except Exception as e:
            print(f"Ошибка загрузки времени: {e}")
            self.ui.RecordTimeComboBox.addItem("Ошибка загрузки")

    # Создание записи
    def on_create_appointment(self):
        if not self.current_doctor_id:
            CustomMessage("Ошибка", "Выберите врача.")
            return
        
        # Получение выбранной записи
        appointment_id = self.ui.RecordTimeComboBox.currentData()
        
        if appointment_id is None:
            CustomMessage("Ошибка", "Выберите время.")
            return
        
        # Получение записи из БД
        appointment = self.session.get(Appointment, appointment_id)
        
        if not appointment or appointment.status != 'available':
            CustomMessage("Ошибка", "Выбранное время больше недоступно.")
            # Загрузка свободных слотов для выбранного врача
            self.load_dates_for_doctor()
            return
        
        user_id = get_current_user()
        
        if not user_id:
            CustomMessage("Ошибка", "Не удалось определить текущего пользователя.")
            return
        
        # Получение пользователя из базы данных
        user = self.session.get(Account, user_id)

        try:
            # Обновление записи
            appointment.account_id = user.id
            appointment.status = 'booked'
            
            # Сохранение изменений в БД
            self.session.commit()

            # Получение ФИО пациента
            fio = f"{user.last_name} {user.first_name} {user.patronymic_name}"
            CustomMessage("Успех", f"Вы успешно записались на приём, {fio}!")
            
            # Загрузка данных врача
            self.load_dates_for_doctor()
            
            # Очистка комбо-бокса времени
            self.ui.RecordTimeComboBox.clear()
        except Exception as e:
            # Откат изменений при ошибке
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при создании записи: {str(e)}")

# ---------- Контроллер страницы записей ----------
class MyRecordsPageController:
    def __init__(self, ui, parent_window: HomeWindow):
        self.ui = ui
        self.parent = parent_window
        # Открытие сессии БД
        self.session = Session()
        
        # Регистрация нажатия кнопок
        self.ui.BackBtnMyRecords.clicked.connect(self.parent.open_home_page)

        # Фотографии
        SVGLoader.load_svg_to_widget("resources/backArrow.svg", self.ui.BackBtnMyRecords, 3, 8)

        # Скролл-арена
        self.scroll_area = QScrollArea(self.ui.MyRecordsPage)
        self.scroll_area.setGeometry(4, 110, 771, 481)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            /* Основной стиль */
            QScrollArea {
                border: none;
                background-color: #F8F9FB;
            }

            /* Стиль для вертикальной полосы прокрутки */
            QScrollBar:vertical {
                background: #F8F9FB;
                width: 10px;
                margin: 5px 0 5px 0;
                border-radius: 5px;
            }

            /* Стиль для вертикального ползунка полосы прокрутки */
            QScrollBar::handle:vertical {
                background: #C9D1DA;
                border-radius: 5px;
                min-height: 20px;
            }

            /* Стиль для вертикального ползунка при наведении курсора */
            QScrollBar::handle:vertical:hover {
                background: #A8B3BF;
            }

            /* Стиль для кнопок вертикальной полосы прокрутки */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0;
            }

            /* Стиль для горизонтальной полосы прокрутки */
            QScrollBar:horizontal {
                background: #F8F9FB;
                height: 10px;
                margin: 0 5px 0 5px;
                border-radius: 5px;
            }

            /* Стиль для горизонтального ползунка полосы прокрутки */
            QScrollBar::handle:horizontal {
                background: #C9D1DA;
                border-radius: 5px;
                min-width: 20px;
            }

            /* Стиль для горизонтального ползунка при наведении курсора */
            QScrollBar::handle:horizontal:hover {
                /*. Установить цвет фона ползунка при наведении */
                background: #A8B3BF;
            }

            /* Стиль для кнопок горизонтальной полосы прокрутки */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 0;
            }
            """)

        # Виджет для содержимого скролл-арены
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        # Компоновщик для содержимого
        self.gridLayout_4 = QGridLayout(self.scroll_content)
        self.gridLayout_4.setContentsMargins(10, 10, 10, 10)
        self.gridLayout_4.setSpacing(15)

    # Загрузка записей
    def reload_appointments(self):
        # Удаление виджетов из компоновщика
        for i in reversed(range(self.gridLayout_4.count())):
            widget = self.gridLayout_4.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        user_id = get_current_user()
        
        # Получение записей пациента
        appointments = self.session.query(Appointment).filter_by(account_id=user_id, status='booked').all()

        if not appointments:
            label = QLabel("Нет активных записей")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                color: rgb(72, 72, 72);
                font-size: 26px;
                background-color: rgba(255, 255, 255, 0);
            """)
            self.gridLayout_4.addWidget(label, 0, 0)
            return

        row, col = 0, 0
        # Создание карточки для каждой записи и добавление в компоновщик
        for app in appointments:
            card = AppointmentCard(app, self)
            self.gridLayout_4.addWidget(card, row, col)
            col += 1
            # Переход на следующую строку после 2 карточек
            if col > 1:
                col = 0
                row += 1


# ---------- Виджет карточки записи ----------
class AppointmentCard(QWidget):
    def __init__(self, appointment: Appointment, controller: MyRecordsPageController):
        super().__init__()
        # Сохранение записи
        self.appointment = appointment
        # Сохранение контроллера для управления логикой
        self.controller = controller
        # Получение сессии БД из контроллера
        self.session = controller.session

        # Включение фона для виджета
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(350, 200)
        self.setStyleSheet("""
            background-color: white;
            border: 1px solid #DEDEDE;
            border-radius: 15px;
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        # Применение эффекта тени к виджету
        self.setGraphicsEffect(shadow)

        # Сохранение доктора из БД
        doctor = self.session.get(Doctor, appointment.doctor_id)

        # Фотография врача
        self.photo_label = QLabel(self)
        self.photo_label.setGeometry(10, 20, 181, 121)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet("border: 0px;")
        # Проверка существования врача и пути к фотографии в БД
        if doctor and doctor.photo_path:
            # Создание фотографии
            pix = QPixmap(doctor.photo_path)
            # Проверка успешной загрузки фотографии из БД
            if not pix.isNull():
                # Масштабирование фотографии
                scaled_pix = pix.scaled(
                    self.photo_label.width(),
                    self.photo_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # Установка масштабированной фотографии
                self.photo_label.setPixmap(scaled_pix)

        # Кнопка отмены записи
        self.cancel_btn = QPushButton("Отменить", self)
        self.cancel_btn.setGeometry(30, 150, 141, 41)
        self.cancel_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                border: 1px solid #2883CD;
                border-radius: 8px;
                background-color: #2A8BD9;
                color: white;
                font-weight: bold;
                transition: 0.2s;
            }
            /* Стиль при наведении крусора */
            QPushButton:hover {
                background-color: #3C9AE6;
            }
            /* Стиль при нажатии курсором */
            QPushButton:pressed {
                background-color: #1E6FBF;
            }
        """)
        
        # Регистрация нажатия кнопок
        self.cancel_btn.clicked.connect(self.cancel_appointment)

        # Имя и фамилия врача
        self.name_label = QLabel(self)
        self.name_label.setGeometry(190, 20, 131, 51)
        self.name_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            color: black;
            border: 1px solid #E9E9E9;
            border-radius: 15px;
            padding: 5px;
        """)

        # Проверка существования врача в БД
        if doctor:
            # Формирование полного имени врача из частей в БД
            full_name = " ".join(
                part for part in [doctor.first_name, doctor.last_name] if part
            )
            # Установка имени врача
            self.name_label.setText(full_name)
        else:
            self.name_label.setText("Неизвестно")

        self.name_label.setWordWrap(True)

        # Специальность врача
        self.spec_label = QLabel(self)
        self.spec_label.setGeometry(190, 80, 131, 51)
        self.spec_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            color: black;
            border: 1px solid #E9E9E9;
            border-radius: 15px;
            padding: 5px;
        """)
        
        # Установка текста специализации врача
        self.spec_label.setText(doctor.specialty.name if doctor and doctor.specialty else "")
        
        self.spec_label.setWordWrap(True)

        # Дата и время записи
        self.datetime_label = QLabel(self)
        self.datetime_label.setGeometry(190, 140, 131, 51)
        self.datetime_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);
            color: black;
            border: 1px solid #E9E9E9;
            border-radius: 15px;
            padding: 5px;
        """)
        # Установка даты и времени
        self.datetime_label.setText(f"{appointment.date.strftime('%d.%m.%Y')} {appointment.time}")
        self.datetime_label.setWordWrap(True)

    # Отмена записи
    def cancel_appointment(self):
        # Освобождение записи
        self.appointment.account_id = None
        self.appointment.status = 'available'
        
        # Сохранение изменений в БД
        self.session.commit()

        CustomMessage("Успех", "Запись отменена, время снова доступно для записи.")
        
        # Обновление записей
        self.controller.reload_appointments()


# ---------- Окно администратора ----------
class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setMinimumSize(1000, 640)
        self.setStyleSheet("background-color: #F8F9FB;")
        
        # Открытие сессии БД
        self.session = Session()
        self.setup_ui()
        
        # Загрузка данных админа
        self.load_admin_data()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        header_layout = QHBoxLayout()
        self.header_label = QLabel("Панель администратора")
        self.header_label.setStyleSheet("color: #1F2937; font-size: 28px; font-weight: bold;")
        header_layout.addWidget(self.header_label)
        
        # Добавление растягивания
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #2A8BD9;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #3C9AE6;
            }
        """)
        # Регистрация нажатия кнопок
        self.refresh_btn.clicked.connect(self.load_admin_data)
        header_layout.addWidget(self.refresh_btn)
        
        # Добавление компоновщика заголовка в основной
        layout.addLayout(header_layout)
        
        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Карточки статистики
        self.total_patients_card = self.create_stat_card("0", "Пациентов")
        self.total_doctors_card = self.create_stat_card("0", "Врачей")
        self.today_appointments_card = self.create_stat_card("0", "Записей на сегодня")
        self.available_slots_card = self.create_stat_card("0", "Свободных слотов")
        
        # Добавление карточек в компоновщик статистики
        stats_layout.addWidget(self.total_patients_card)
        stats_layout.addWidget(self.total_doctors_card)
        stats_layout.addWidget(self.today_appointments_card)
        stats_layout.addWidget(self.available_slots_card)
        
        # Добавление компоновщика статистики в основной
        layout.addLayout(stats_layout)
        
        # Кнопки действий админа
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        self.add_doctor_btn = QPushButton("+ Добавить врача")
        self.add_doctor_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #2A8BD9;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #3C9AE6;
            }
        """)
        # Регистрация нажатия кнопок
        self.add_doctor_btn.clicked.connect(self.open_add_doctor_dialog)
        
        self.add_slot_btn = QPushButton("+ Добавить слоты")
        self.add_slot_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #34D399;
            }
        """)
        # Регистрация нажатия кнопок
        self.add_slot_btn.clicked.connect(self.open_add_slot_dialog)
        
        actions_layout.addWidget(self.add_doctor_btn)
        actions_layout.addWidget(self.add_slot_btn)
        
        # Добавление растягивания
        actions_layout.addStretch()
        
        # Добавление компоновщика действий в основной
        layout.addLayout(actions_layout)
        
        # Панель поиска и сортировки для врачей
        search_sort_layout = QHBoxLayout()
        search_sort_layout.setSpacing(10)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по врачам...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2A8BD9;
            }
        """)
        # Регистрация изменения текста поиска
        self.search_input.textChanged.connect(self.filter_doctors)
        
        # Комбо-бокс сортировки
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сортировка: ФИО А-Я", "Сортировка: ФИО Я-А", "Сортировка: Специальность", "Сортировка: Записи ↑", "Сортировка: Записи ↓"])
        self.sort_combo.setStyleSheet(StyleManager.get_combo_box_style())
        # Регистрация изменения сортировки
        self.sort_combo.currentIndexChanged.connect(self.sort_doctors)
        
        search_sort_layout.addWidget(self.search_input)
        search_sort_layout.addWidget(self.sort_combo)
        search_sort_layout.addStretch()
        
        # Добавление панели поиска и сортировки в основной компоновщик
        layout.addLayout(search_sort_layout)
        
        # Вкладки админа
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            /* Стиль для панели */
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
            }
            /* Стиль для отдельных вкладок в панели */
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #6B7280;
                padding: 12px 24px;
                margin: 2px;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            /* Стиль для активной вкладка */
            QTabBar::tab:selected {
                background-color: #2A8BD9;
                color: white;
            }
        """)
        
        # Вкладка врачей
        self.doctors_tab = QWidget()
        doctors_layout = QVBoxLayout(self.doctors_tab)
        # Таблица для врачей
        self.doctors_table = QTableWidget()
        # Количество столбцов в таблице 
        self.doctors_table.setColumnCount(5)
        # Заголовки столбцов
        self.doctors_table.setHorizontalHeaderLabels(["ФИО", "Специальность", "Кол-во записей", "Статус", "Действия"])
        # Режим изменения размера столбцов
        self.doctors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Добавление таблицы в компоновщик
        doctors_layout.addWidget(self.doctors_table)
        
        # Вкладка записей
        self.appointments_tab = QWidget()
        appointments_layout = QVBoxLayout(self.appointments_tab)
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(8)
        self.appointments_table.setHorizontalHeaderLabels(["Пациент", "Врач", "Специальность", "Дата", "Время", "Телефон", "Статус", "Действия"])
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        appointments_layout.addWidget(self.appointments_table)
        
        # Вкладка последней активности
        self.activity_tab = QWidget()
        activity_layout = QVBoxLayout(self.activity_tab)
        activity_label = QLabel("Последняя активность")
        activity_label.setStyleSheet("color: #374151; font-size: 16px; font-weight: bold;")
        activity_layout.addWidget(activity_label)
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setStyleSheet("background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px;")
        activity_layout.addWidget(self.activity_text)
        
        # Названия вкладок
        self.tab_widget.addTab(self.doctors_tab, "Врачи")
        self.tab_widget.addTab(self.appointments_tab, "Записи")
        self.tab_widget.addTab(self.activity_tab, "Активность")
        
        # Добавление виджета вкладок в основной
        layout.addWidget(self.tab_widget)

    # Создание карточек статистики
    def create_stat_card(self, value, label):
        card = QWidget()
        card.setStyleSheet("background-color: white; border: 1px solid #E5E7EB; border-radius: 10px;")
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #111827; font-size: 32px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("color: #6B7280; font-size: 14px;")
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_label)
        
        return card
    
    # Загрузка данных админа
    def load_admin_data(self):
        self.load_statistics()
        self.load_doctors_table()
        self.load_appointments_table()
        self.load_recent_activity()

    # Загрузка статистики
    def load_statistics(self):
        # Выгрузка статистики из БД
        try:
            # Количество пациентов
            total_patients = self.session.query(Account).count()
            # Обновление значения
            self.total_patients_card.layout().itemAt(0).widget().setText(str(total_patients))
            
            # Количество докторов
            total_doctors = self.session.query(Doctor).count()
            # Обновление значения
            self.total_doctors_card.layout().itemAt(0).widget().setText(str(total_doctors))
            
            # Количество активных записей на сегодня
            today_appointments = self.session.query(Appointment).filter(
                Appointment.date == date.today(),
                Appointment.status == 'booked'
            ).count()
            # Обновление значения
            self.today_appointments_card.layout().itemAt(0).widget().setText(str(today_appointments))
            
            # Количество доступных записей
            available_appointments = self.session.query(Appointment).filter(
                Appointment.status == 'available'
            ).count()
            # Обновление значения
            self.available_slots_card.layout().itemAt(0).widget().setText(str(available_appointments))
        
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    # Загрузка врачей
    def load_doctors_table(self):
        # Выгрузка врачей из БД
        try:
            # Получение врачей
            doctors = self.session.query(Doctor).all()
            # Сохранение всех врачей для фильтрации и сортировки
            self.all_doctors = doctors
            # Применение фильтрации и сортировки
            self.apply_doctors_filters()
        
        except Exception as e:
            print(f"Ошибка загрузки таблицы врачей: {e}")

    # Применение фильтров и сортировки к врачам
    def apply_doctors_filters(self):
        if not hasattr(self, 'all_doctors'):
            return
            
        filtered_doctors = self.all_doctors.copy()
        
        # Применение поискового фильтра
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered_doctors = [
                doctor for doctor in filtered_doctors
                if (search_text in doctor.last_name.lower() or 
                    search_text in doctor.first_name.lower() or
                    search_text in f"{doctor.last_name} {doctor.first_name}".lower() or
                    (doctor.specialty and search_text in doctor.specialty.name.lower()))
            ]
        
        # Применение сортировки
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:  # ФИО А-Я
            filtered_doctors.sort(key=lambda d: f"{d.last_name} {d.first_name}")
        elif sort_index == 1:  # ФИО Я-А
            filtered_doctors.sort(key=lambda d: f"{d.last_name} {d.first_name}", reverse=True)
        elif sort_index == 2:  # Специальность
            filtered_doctors.sort(key=lambda d: d.specialty.name if d.specialty else "")
        elif sort_index == 3:  # Записи ↑
            filtered_doctors.sort(key=lambda d: self.get_doctor_appointment_count(d.id))
        elif sort_index == 4:  # Записи ↓
            filtered_doctors.sort(key=lambda d: self.get_doctor_appointment_count(d.id), reverse=True)
        
        # Обновление таблицы с отфильтрованными данными
        self.update_doctors_table(filtered_doctors)

    # Получение количества записей врача
    def get_doctor_appointment_count(self, doctor_id):
        return self.session.query(Appointment).filter_by(
            doctor_id=doctor_id, 
            status='booked'
        ).count()

    # Обновление таблицы врачей
    def update_doctors_table(self, doctors):
        # Количество строк в таблице
        self.doctors_table.setRowCount(len(doctors))
        
        # Настройка режима изменения размеров столбцов
        header = self.doctors_table.horizontalHeader()
        # Растягивание столбцов, кроме последнего
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        # Фиксированный размер для 4 столбца
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        # Установка фиксированной ширины 4 столбца
        table_width = self.doctors_table.width()
        actions_column_width = table_width // 3
        self.doctors_table.setColumnWidth(4, actions_column_width)
        
        self.doctors_table.setStyleSheet("""
            /* Основной стиль */
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #F3F4F6;
                font-size: 14px;
            }
            /* Стиль для ячеек */
            QTableWidget::item {
                color: black;
                border-bottom: 1px solid #F3F4F6;
                padding: 10px;
                font-size: 14px;
            }
            /* Стиль для заголовков */
            QHeaderView::section {
                background-color: #F9FAFB;
                color: black;
                padding: 15px 10px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        # Заполнение таблицы врачами
        for row, doctor in enumerate(doctors):
            # Установка ширины строк
            self.doctors_table.setRowHeight(row, 70)
            
            # ФИО врачей
            fio = f"{doctor.last_name} {doctor.first_name}"
            # Создание элемента таблицы
            fio_item = QTableWidgetItem(fio)
            fio_item.setForeground(QColor("black"))
            # Установка элемента в таблицу
            self.doctors_table.setItem(row, 0, fio_item)
            
            # Специальность врачей
            spec_name = doctor.specialty.name if doctor.specialty else "Не указана"
            # Создание элемента таблицы
            spec_item = QTableWidgetItem(spec_name)
            spec_item.setForeground(QColor("black"))
            # Установка элемента в таблицу
            self.doctors_table.setItem(row, 1, spec_item)
            
            # Количество активных записей ко врачу
            app_count = self.get_doctor_appointment_count(doctor.id)
            # Создание элемента таблицы
            count_item = QTableWidgetItem(str(app_count))
            count_item.setForeground(QColor("black"))
            # Установка элемента в таблицу
            self.doctors_table.setItem(row, 2, count_item)
            
            # Статус записи
            # Получение статуса врача
            status = "Активен" if getattr(doctor, 'is_active', True) else "Неактивен"
            # Создание элемента таблицы
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("black"))
            # Установка элемента в таблицу
            self.doctors_table.setItem(row, 3, status_item)
            
            # Виджет с кнопками действий
            actions_widget = self.create_doctor_actions_widget(doctor.id)
            self.doctors_table.setCellWidget(row, 4, actions_widget)

    # Фильтрация врачей
    def filter_doctors(self):
        self.apply_doctors_filters()

    # Сортировка врачей
    def sort_doctors(self):
        self.apply_doctors_filters()
        
    # Создание виджета с кнопками действий для врача
    def create_doctor_actions_widget(self, doctor_id):
        # Создание виджета для кнопок
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Кнопка редактирования врача
        edit_btn = QPushButton("Редакт.")
        edit_btn.setFixedSize(70, 32)
        edit_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #34D399;
            }
            /* Стиль при нажатии курсором */
            QPushButton:pressed {
                background-color: #059669;
            }
        """)
        
        # Кнопка удаления врача
        delete_btn = QPushButton("Удалить")
        delete_btn.setFixedSize(70, 32)
        delete_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #F87171;
            }
            /* Стиль при нажатии курсором */
            QPushButton:pressed {
                background-color: #DC2626;
            }
        """)
        
        # Регистрация нажатия кнопок
        edit_btn.clicked.connect(lambda: self.edit_doctor(doctor_id))
        delete_btn.clicked.connect(lambda: self.delete_doctor(doctor_id))
        
        # Добавление кнопок в компоновщик
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return widget

    # Редактирование врача
    def edit_doctor(self, doctor_id):
        try:
            # Получение врача из БД
            doctor = self.session.get(Doctor, doctor_id)
            if not doctor:
                CustomMessage("Ошибка", "Врач не найден")
                return
            
            # Открытие диалогового окна редактирования врача
            dialog = EditDoctorDialog(self, doctor)
            # Обновление данных при успешной работе окна
            if dialog.exec():
                self.load_doctors_table()
                self.load_statistics()
        
        except Exception as e:
            CustomMessage("Ошибка", f"Ошибка при редактировании врача: {str(e)}")

    # Удаление врача
    def delete_doctor(self, doctor_id):
        try:
            # Получение врача из БД
            doctor = self.session.get(Doctor, doctor_id)
            if not doctor:
                CustomMessage("Ошибка", "Врач не найден")
                return
            
            # Проверка наличия активных записей у врача
            active_appointments = self.session.query(Appointment).filter_by(
                doctor_id=doctor_id, 
                status='booked'
            ).count()
            
            if active_appointments > 0:
                CustomMessage("Ошибка", f"Невозможно удалить врача. У него есть {active_appointments} активных записей.")
                return
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Вы уверены, что хотите удалить врача {doctor.last_name} {doctor.first_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            # Удаление врача при подтверждении
            if reply == QMessageBox.StandardButton.Yes:
                # Удаление всех записей врача
                self.session.query(Appointment).filter_by(doctor_id=doctor_id).delete()
                # Удаление врача
                self.session.delete(doctor)
                # Сохранение изменений в БД
                self.session.commit()
                
                CustomMessage("Успех", "Врач успешно удален")
                # Обновление таблицы врачей
                self.load_doctors_table()
                # Обновление статистики
                self.load_statistics()
        
        except Exception as e:
            # Откат изменений в случае ошибки
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при удалении врача: {str(e)}")

    # Загрузка записей
    def load_appointments_table(self):
        # Выгрузка записей из БД
        try:
            # Получение и сортировка активных записей
            appointments = self.session.query(Appointment).filter(
                Appointment.status == 'booked'
            ).order_by(Appointment.date.desc()).limit(50).all()
            
            # Количество строк в таблице
            self.appointments_table.setRowCount(len(appointments))
            
            # Стили для заголовков таблицы
            header = self.appointments_table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { color: black; background-color: #F9FAFB; }")
            
            self.appointments_table.verticalHeader().setStyleSheet("QHeaderView::section { color: black; background-color: #F9FAFB; }")
            
            # Заполнение таблицы записями
            for row, app in enumerate(appointments):
                # Установка ширины строк
                self.appointments_table.setRowHeight(row, 50)
                
                # Получение пациента
                patient = self.session.get(Account, app.account_id)
                # ФИО пациента
                if patient:
                    patient_name = f"{patient.last_name} {patient.first_name} {patient.patronymic_name or ''}"
                    patient_phone = patient.phone_number or "Не указан"
                else:
                    patient_name = "Неизвестно"
                    patient_phone = "Не указан"
                
                # Создание элемента таблицы
                patient_item = QTableWidgetItem(patient_name)
                patient_item.setForeground(QColor("black"))
                # Установка элемента в таблицу
                self.appointments_table.setItem(row, 0, patient_item)
                
                # Врач
                doctor = self.session.get(Doctor, app.doctor_id)
                # ФИО врача
                if doctor:
                    doctor_name = f"{doctor.last_name} {doctor.first_name}"
                    doctor_spec = doctor.specialty.name if doctor.specialty else "Не указана"
                else:
                    doctor_name = "Неизвестно"
                    doctor_spec = "Не указана"
                
                # Создание элемента таблицы
                doctor_item = QTableWidgetItem(doctor_name)
                doctor_item.setForeground(QColor("black"))
                # Установка элемента в таблицу
                self.appointments_table.setItem(row, 1, doctor_item)
                
                # Специальность врача
                spec_item = QTableWidgetItem(doctor_spec)
                spec_item.setForeground(QColor("black"))
                self.appointments_table.setItem(row, 2, spec_item)
                
                # Дата записи
                # Создание элемента таблицы
                date_item = QTableWidgetItem(app.date.strftime("%d.%m.%Y"))
                date_item.setForeground(QColor("black"))
                # Установка элемента в таблицу
                self.appointments_table.setItem(row, 3, date_item)
                
                # Время записи
                # Создание элемента таблицы
                time_item = QTableWidgetItem(str(app.time))
                time_item.setForeground(QColor("black"))
                # Установка элемента в таблицу
                self.appointments_table.setItem(row, 4, time_item)
                
                # Телефон пациента
                phone_item = QTableWidgetItem(patient_phone)
                phone_item.setForeground(QColor("black"))
                self.appointments_table.setItem(row, 5, phone_item)
                
                # Статус записи
                # Создание элемента таблицы
                status_item = QTableWidgetItem("Активна")
                status_item.setForeground(QColor("black"))
                # Установка элемента в таблицу
                self.appointments_table.setItem(row, 6, status_item)
                
                # Кнопка отмены записи
                cancel_btn = QPushButton("Отмена")
                cancel_btn.setFixedSize(80, 32)
                cancel_btn.setStyleSheet("""
                    /* Основной стиль */
                    QPushButton {
                        background-color: #2A8BD9;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    /* Стиль при наведении курсора */
                    QPushButton:hover {
                        background-color: #3C9AE6;
                    }
                    /* Стиль при нажатии курсором */
                    QPushButton:pressed {
                        background-color: #1E6FBF;
                    }
                """)
                # Регистрация нажатия кнопок
                cancel_btn.clicked.connect(lambda checked, app_id=app.id: self.cancel_appointment(app_id))
                
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.addWidget(cancel_btn)
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                # Установка виджета в таблицу
                self.appointments_table.setCellWidget(row, 7, widget)
        
        except Exception as e:
            print(f"Ошибка загрузки таблицы записей: {e}")

    # Отмена записи
    def cancel_appointment(self, appointment_id):
        try:
            # Получение записи по коду
            appointment = self.session.get(Appointment, appointment_id)
            if not appointment:
                CustomMessage("Ошибка", "Запись не найдена")
                return
            
            # Сохранение пациента и врача
            patient = self.session.get(Account, appointment.account_id)
            doctor = self.session.get(Doctor, appointment.doctor_id)
            
            # Освобождение записи
            appointment.account_id = None
            appointment.status = 'available'
            
            # Сохранение изменений в БД
            self.session.commit()
            
            if patient and doctor:
                patient_name = f"{patient.last_name} {patient.first_name}"
                doctor_name = f"{doctor.last_name} {doctor.first_name}"
                cancel_info = f"✗ Администратор отменил запись {patient_name} к {doctor_name} на {appointment.date.strftime('%d.%m.%Y')} {appointment.time}\n"
                
                # Обновление активности
                current_text = self.activity_text.toPlainText()
                self.activity_text.setPlainText(cancel_info + current_text)
            
            CustomMessage("Успех", "Запись успешно отменена")
            
            # Обновление записей в таблице
            self.load_appointments_table()
            # Обновление статистики
            self.load_statistics()
        
        except Exception as e:
            # Откат изменений при ошибке
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при отмене записи: {str(e)}")

    # Загрузка недавней активности
    def load_recent_activity(self):
        try:
            # Выгрузка недавней активности из БД
            recent_appointments = self.session.query(Appointment).filter(
                Appointment.status == 'booked'
            ).order_by(
                Appointment.date.desc(), Appointment.time.desc()
            ).limit(10).all()
            
            activity_text = ""
            
            # Формирование текста недавней активностью
            for app in recent_appointments:
                patient = self.session.get(Account, app.account_id)
                doctor = self.session.get(Doctor, app.doctor_id)
                
                # Заполнение недавней активностью
                if patient and doctor:
                    patient_name = f"{patient.last_name} {patient.first_name}"
                    doctor_name = f"{doctor.last_name} {doctor.first_name}"
                    activity_text += f"✓ {patient_name} записался к {doctor_name} на {app.date.strftime('%d.%m.%Y')} {app.time}\n"
            
            # Установка текста активности
            self.activity_text.setPlainText(activity_text)
            self.activity_text.setStyleSheet("color: black; background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px;")
        
        except Exception as e:
            print(f"Ошибка загрузки активности: {e}")
            # Установка текста ошибки
            self.activity_text.setPlainText("Ошибка загрузки данных активности")
            self.activity_text.setStyleSheet("color: black; background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px;")

    # Открытие диалогового окна добавления врача
    def open_add_doctor_dialog(self):
        dialog = AddDoctorDialog(self)
        # Обновление данных при успешной работе окна
        if dialog.exec():
            self.load_doctors_table()
            self.load_statistics()

    # Открытие диалогового окна добавления слота записи
    def open_add_slot_dialog(self):
        dialog = AddSlotDialog(self)
        # Обновление данных при успешной работе окна
        if dialog.exec():
            self.load_statistics()

# ---------- Окно редактирования врача ----------
class EditDoctorDialog(QDialog):
    def __init__(self, parent, doctor):
        super().__init__(parent)
        self.parent = parent
        self.doctor = doctor
        # Получение сессии БД из родительского окна
        self.session = parent.session
        self.ui = Ui_EditDoctorDialog()
        self.ui.setupUi(self)
        
        # Применение стилей
        self.apply_styles()
        
        # Настройка соединений
        self.setup_connections()
        
        # Загрузка данных врача
        self.load_doctor_data()
        
        # Загрузка специальностей
        self.load_specialties()

    # Применение стилей
    def apply_styles(self):
        # Применение стиля к комбо-боксу специальностей
        self.ui.specialtyCombo.setStyleSheet(StyleManager.get_combo_box_style())

    # Настройка соединений
    def setup_connections(self):
        # Форматирование поля телефона
        self.ui.phoneInput.textChanged.connect(lambda text: PhoneFormatter.on_phone_text_changed(self.ui.phoneInput, text))
        
        # Регистрация нажатия кнопок
        self.ui.saveButton.clicked.connect(self.save_doctor)
        self.ui.cancelButton.clicked.connect(self.reject)

    # Загрузка специальностей
    def load_specialties(self):
        # Выгрузка специальностей из БД
        specialties = self.session.query(Specialty).all()
        # Добавление каждой специальности в комбо-бокс
        for spec in specialties:
            self.ui.specialtyCombo.addItem(spec.name, spec.id)

    # Загрузка данных врача
    def load_doctor_data(self):
        # Установка данных врача в поля
        self.ui.lastNameInput.setText(self.doctor.last_name or "")
        self.ui.firstNameInput.setText(self.doctor.first_name or "")
        self.ui.phoneInput.setText(self.doctor.phone_number or "")
        self.ui.photoPathInput.setText(self.doctor.photo_path or "")
        
        # Установка специальности врача
        if self.doctor.specialty_id:
            index = self.ui.specialtyCombo.findData(self.doctor.specialty_id)
            if index >= 0:
                self.ui.specialtyCombo.setCurrentIndex(index)

    # Сохранение изменений врача
    def save_doctor(self):
        # Получение и очистка данных из полей
        last_name = self.ui.lastNameInput.text().strip()
        first_name = self.ui.firstNameInput.text().strip()
        specialty_id = self.ui.specialtyCombo.currentData()
        phone = self.ui.phoneInput.text().strip()
        photo_path = self.ui.photoPathInput.text().strip()
        
        if not all([last_name, first_name, specialty_id]):
            CustomMessage("Ошибка", "Заполните обязательные поля (Фамилия, Имя, Специальность)")
            return
        
        if phone:
            digits_phone = ''.join(filter(str.isdigit, phone))
            if len(digits_phone) != 11:
                CustomMessage("Ошибка", "Введите полный номер телефона")
                return
        
        try:
            # Обновление данных врача
            self.doctor.last_name = last_name
            self.doctor.first_name = first_name
            self.doctor.specialty_id = specialty_id
            self.doctor.phone_number = phone if phone else None
            self.doctor.photo_path = photo_path if photo_path else None
            
            # Сохранение изменений в БД
            self.session.commit()
            
            CustomMessage("Успех", "Данные врача успешно обновлены")
            self.accept()
        
        except Exception as e:
            # Откат изменений в случае ошибки
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при сохранении: {str(e)}")

# ---------- Окно добавления врача ----------
class AddDoctorDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Получение сессии БД из родительского окна
        self.session = parent.session
        self.ui = Ui_AddDoctorDialog()
        self.ui.setupUi(self)
        
        # Регистрация нажатия кнопок
        self.ui.saveButton.clicked.connect(self.save_doctor)
        self.ui.cancelButton.clicked.connect(self.reject)
        
        # Загрузка специальностей
        self.load_specialties()

    # Загрузка специальностей
    def load_specialties(self):
        # Выгрузка специальностей из БД
        specialties = self.session.query(Specialty).all()
        # Добавление каждой специальности в комбо-бокс
        for spec in specialties:
            self.ui.specialtyCombo.addItem(spec.name, spec.id)

    # Добавление врача
    def save_doctor(self):
        # Получение и очистка данных из полей
        last_name = self.ui.lastNameInput.text().strip()
        first_name = self.ui.firstNameInput.text().strip()
        specialty_id = self.ui.specialtyCombo.currentData()
        
        if not all([last_name, first_name, specialty_id]):
            CustomMessage("Ошибка", "Заполните обязательные поля (Фамилия, Имя, Специальность)")
            return
        
        try:
            # Сохранение данных врача
            doctor_data = {
                'last_name': last_name,
                'first_name': first_name,
                'specialty_id': specialty_id
            }
            
            # Получение путя к фотографии врача
            photo_path = self.ui.photoPathInput.text().strip()
            # Добавление в данные
            if photo_path and hasattr(Doctor, 'photo_path'):
                doctor_data['photo_path'] = photo_path
            
            # Установка статуса при наличии
            if hasattr(Doctor, 'is_active'):
                doctor_data['is_active'] = True
            
            # Создание врача
            new_doctor = Doctor(**doctor_data)
            
            # Добавление врача в БД
            self.session.add(new_doctor)
            # Сохранение изменений в БД
            self.session.commit()
            
            CustomMessage("Успех", "Врач успешно добавлен")
            self.accept()
        
        except Exception as e:
            # Откат изменений в случае ошибки
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при сохранении: {str(e)}")

# ---------- Окно добавления слота записи ----------
class AddSlotDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Получение сессии БД из родительского окна
        self.session = parent.session
        self.ui = Ui_AddSlotDialog()
        self.ui.setupUi(self)
        
        # Установка текущей даты по умолчанию
        self.ui.dateEdit.setDate(date.today())
        # Устанавка время по умолчанию
        self.ui.timeEdit.setTime(datetime.strptime("09:00", "%H:%M").time())
        
        # Регистрация нажатия кнопок
        self.ui.saveButton.clicked.connect(self.create_slot)
        self.ui.cancelButton.clicked.connect(self.reject)
        
        # Загрузка врачей
        self.load_doctors()

    # Загрузка врачей из БД
    def load_doctors(self):
        try:
            # Выгрузка только активных врачей
            if hasattr(Doctor, 'is_active'):
                doctors = self.session.query(Doctor).filter_by(is_active=True).all()
            # Выгрузка всех врачей
            else:
                doctors = self.session.query(Doctor).all()
            
            # Добавление каждого врача в комбо-бокс
            for doctor in doctors:
                last_name = getattr(doctor, 'last_name', '')
                first_name = getattr(doctor, 'first_name', '')
                name = f"{last_name} {first_name}"
                # Добавление врачей в комбо-бокс
                self.ui.doctorCombo.addItem(name, doctor.id)
        except Exception as e:
            print(f"Ошибка загрузки врачей: {e}")
            # Выгрузка всех врачей при ошибке
            doctors = self.session.query(Doctor).all()
            for doctor in doctors:
                last_name = getattr(doctor, 'last_name', '')
                first_name = getattr(doctor, 'first_name', '')
                name = f"{last_name} {first_name}"
                # Добавление врачей в комбо-бокс
                self.ui.doctorCombo.addItem(name, doctor.id)

    # Создание слота записи
    def create_slot(self):
        # Получение данных из полей
        doctor_id = self.ui.doctorCombo.currentData()
        slot_date = self.ui.dateEdit.date().toPyDate()
        slot_time = self.ui.timeEdit.time().toString("HH:mm")
        
        if not doctor_id:
            CustomMessage("Ошибка", "Выберите врача")
            return
        
        # Добавление записи в БД
        try:
            # Проверка наличия создаваемой записи в БД
            existing = self.session.query(Appointment).filter_by(
                doctor_id=doctor_id,
                date=slot_date,
                time=slot_time
            ).first()
            
            if existing:
                CustomMessage("Ошибка", "Такая запись уже существует")
                return
            
            # Сохранение создаваемой записи
            new_appointment = Appointment(
                doctor_id=doctor_id,
                date=slot_date,
                time=slot_time,
                status='available',
                account_id=None
            )
            
            # Добавление новой записи в БД
            self.session.add(new_appointment)
            # Сохранение изменений в БД
            self.session.commit()
            
            CustomMessage("Успех", "Запись успешно создана")
            self.accept()
        
        except Exception as e:
            # Откат изменений в случае ошибки
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при создании записи: {str(e)}")


# ---------- Окно врача ----------
class DoctorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DoctorWindow()
        self.ui.setupUi(self)
        self.setMinimumSize(1000, 640)
        # Открытие сессии БД
        self.session = Session()
        # Обновление
        self.setup_connections()
        # Инициализация таблиц
        self.setup_tables()
        # Загрузка данных врача
        self.load_doctor_data()

    # Обновление
    def setup_connections(self):
        # Регистрация нажатия кнопок
        self.ui.refreshBtn.clicked.connect(self.load_doctor_data)

    # Инициализация таблиц
    def setup_tables(self):
        # Установка заголовков для таблицы сегодняшних записей
        self.ui.todayTable.setColumnCount(7)
        self.ui.todayTable.setHorizontalHeaderLabels([
            "Пациент", "Дата рождения", "СНИЛС", "Телефон", "Время", "Статус", "Действия"
        ])
        
        # Установка заголовков для таблицы всех записей
        self.ui.allTable.setColumnCount(8)
        self.ui.allTable.setHorizontalHeaderLabels([
            "Пациент", "Дата рождения", "СНИЛС", "Телефон", "Дата", "Время", "Статус", "Действия"
        ])

    # Загрузка данных врача
    def load_doctor_data(self):
        # Получение кода врача
        doctor_id = get_current_doctor()
        
        if not doctor_id:
            CustomMessage("Ошибка", "Не удалось определить врача")
            return
        
        # Получение врача из БД
        doctor = self.session.get(Doctor, doctor_id)
        # Вывод информации о враче
        if doctor:
            self.ui.doctorNameLabel.setText(f"Добро пожаловать, {doctor.first_name} {doctor.last_name}!")
            spec_name = doctor.specialty.name if doctor.specialty else "Не указана"
            self.ui.doctorSpecLabel.setText(f"Специальность: {spec_name}")
        
        # Загрузка статистики врача
        self.load_statistics()
        # Загрузка записей ко врачу на сегодня
        self.load_today_appointments()
        # Загрузка всех записей врача
        self.load_all_appointments()

    # Загрузка статистики врача
    def load_statistics(self):
        # Получение код врача
        doctor_id = get_current_doctor()
        if not doctor_id:
            return
        
        # Выгрузка статистики врача
        try:
            # Записи ко врачу на сегодня
            today_appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == date.today(),
                Appointment.status == 'booked'
            ).count()
            # Установка значения
            self.ui.todayAppointmentsValue.setText(str(today_appointments))
            
            # Всего активных записей ко врачу
            total_appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.status == 'booked'
            ).count()
            # Установка значения
            self.ui.totalAppointmentsValue.setText(str(total_appointments))
            
            # Завершённые записи
            completed = today_appointments // 2
            # Установка значения
            self.ui.completedValue.setText(str(completed))
            
            # Отменённые записи
            cancelled = today_appointments // 4
            # Установка значения
            self.ui.cancelledValue.setText(str(cancelled))
        
        except Exception as e:
            print(f"Ошибка загрузки статистики врача: {e}")

    # Загрузка записей на сегодня
    def load_today_appointments(self):
        # Получение код врача
        doctor_id = get_current_doctor()
        if not doctor_id:
            return
        
        try:
            # Получение только активных записей на сегодня
            appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == date.today(),
                Appointment.status == 'booked'
            ).order_by(Appointment.time).all()
            
            print(f"Найдено активных записей на сегодня: {len(appointments)}")
            
            # Количество строк
            self.ui.todayTable.setRowCount(len(appointments))
            
            # Добавление записей в таблицу
            for row, app in enumerate(appointments):
                # Ширина строк
                self.ui.todayTable.setRowHeight(row, 100)
                # Заполнение строк
                self.fill_appointment_row(self.ui.todayTable, row, app, include_date=False)

        # Ошибка при загрузке записей ко врачу на сегодня
        except Exception as e:
            print(f"Ошибка загрузки сегодняшних записей: {e}")

    # Загрузка всех записей ко врачу
    def load_all_appointments(self):
        # Получение кода врача
        doctor_id = get_current_doctor()
        if not doctor_id:
            return
        
        try:
            # Получение только активных записей
            appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.status == 'booked'
            ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
            
            print(f"Найдено всех активных записей: {len(appointments)}")
            
            # Количество строк
            self.ui.allTable.setRowCount(len(appointments))
            
            # Добавление записей в таблицу
            for row, app in enumerate(appointments):
                # Ширина строк
                self.ui.allTable.setRowHeight(row, 100)
                # Заполнение строк
                self.fill_appointment_row(self.ui.allTable, row, app, include_date=True)
        
        except Exception as e:
            print(f"Ошибка загрузки всех записей: {e}")

    # Заполнение строк
    def fill_appointment_row(self, table, row, appointment, include_date=False):
        # Получение пациента
        patient = self.session.get(Account, appointment.account_id)
        
        # Получение данных о пациенте
        if patient:
            patient_name = f"{patient.last_name} {patient.first_name} {patient.patronymic_name or ''}"
            birth_date = patient.birth_date.strftime("%d.%m.%Y") if patient.birth_date else "Не указана"
            snils = patient.snils or "Не указан"
            phone = patient.phone_number or "Не указан"
        else:
            patient_name = "Неизвестно"
            birth_date = "Не указана"
            snils = "Не указан"
            phone = "Не указан"
        
        # Заполнение столбцов данными о пациенте
        table.setItem(row, 0, self.create_table_item(patient_name))
        table.setItem(row, 1, self.create_table_item(birth_date))
        table.setItem(row, 2, self.create_table_item(snils))
        table.setItem(row, 3, self.create_table_item(phone))
        
        # Установка даты и времени в отдельные столбцы при необходимости
        if include_date:
            # Для таблицы всех записей
            table.setItem(row, 4, self.create_table_item(appointment.date.strftime("%d.%m.%Y")))
            table.setItem(row, 5, self.create_table_item(str(appointment.time)))
            table.setItem(row, 6, self.create_table_item("Активна"))
            
            # Создание виджета с кнопками
            actions_widget = self.create_actions_widget(appointment.id)
            table.setCellWidget(row, 7, actions_widget)
        else:
            # Для таблицы сегодняшних записей
            table.setItem(row, 4, self.create_table_item(str(appointment.time)))
            table.setItem(row, 5, self.create_table_item("Активна"))
            
            # Создание виджета с кнопками
            actions_widget = self.create_actions_widget(appointment.id)
            table.setCellWidget(row, 6, actions_widget)

    def create_table_item(self, text):
        # Создание элемента таблицы
        item = QTableWidgetItem(text)
        item.setForeground(QColor("black"))
        return item

    def create_actions_widget(self, appointment_id):
        # Создание виджета для кнопок
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Кнопка отмены записи
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(70, 32)
        cancel_btn.setStyleSheet("""
            /* Основной стиль */
            QPushButton {
                background-color: #2A8BD9;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            /* Стиль при наведении курсора */
            QPushButton:hover {
                background-color: #3C9AE6;
            }
            /* Стиль при нажатии курсором */
            QPushButton:pressed {
                background-color: #1E6FBF;
            }
        """)
        
        # Регистрация нажатия кнопок
        cancel_btn.clicked.connect(lambda: self.cancel_appointment(appointment_id))
        
        # Добавление кнопки в компоновщик
        layout.addWidget(cancel_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return widget

    # Отмена записи
    def cancel_appointment(self, appointment_id):
        try:
            # Получение записи
            appointment = self.session.get(Appointment, appointment_id)
            if not appointment:
                CustomMessage("Ошибка", "Запись не найдена")
                return
            
            # Получение пациента
            patient = self.session.get(Account, appointment.account_id)
            
            # Имя пациента
            if patient:
                patient_name = f"{patient.last_name} {patient.first_name}"
            else:
                patient_name = "Неизвестный пациент"
            
            # Освобождение записи
            appointment.account_id = None
            appointment.status = 'available'
            
            # Сохранение изменений в БД
            self.session.commit()
            
            CustomMessage("Успех", f"Запись пациента {patient_name} отменена. Запись возвращена в расписание.")
            # Обновление данных врача
            self.load_doctor_data()
        
        except Exception as e:
            # Откат изменений в случае ошибки
            self.session.rollback()
            CustomMessage("Ошибка", f"Ошибка при отмене записи: {str(e)}")


# ---------- Запуск приложения ----------
if __name__ == "__main__":
    # Инициализация БД
    init_db()
    # Вставка данных в БД
    fill_data()
    app = QApplication(sys.argv)
    # Начальное окно
    window = AuthorizationWindow()
    window.show()
    # Запуск приложения
    sys.exit(app.exec())