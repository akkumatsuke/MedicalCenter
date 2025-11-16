# Глобальная переменная для хранения кода текущего пользователя
current_user_id = None
# Глобальная переменная для хранения кода текущего врача
_current_doctor_id = None

# Получение кода текущего пользователя
def get_current_user() -> int | None:
    return current_user_id

# Получение кода текущего врача
def get_current_doctor():
    return _current_doctor_id

# Установка кода текущего пользователя
def set_current_user(user_id: int):
    global current_user_id
    current_user_id = user_id

# Установка кода текущего врача
def set_current_doctor(doctor_id):
    global _current_doctor_id
    _current_doctor_id = doctor_id

# Очистка кода текущего пользователя
def clear_current_user():
    global current_user_id
    current_user_id = None

# Очистка кода текущего врача
def clear_current_doctor():
    global _current_doctor_id
    _current_doctor_id = None