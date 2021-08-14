# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:13:27 2021

@author: yaros
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
import sys
import monitoringbackend as mbd

class SignIn(QtWidgets.QWidget):
    """"
    Окно авторизации
    """
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle('Авторизация')
        
        # Объекты
        self.header = SignInHeader()
        self.login_label = QtWidgets.QLabel('Логин')
        self.login_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.login_add = QtWidgets.QLineEdit()
        self.login_add.setAlignment(QtCore.Qt.AlignHCenter)
        self.password_label = QtWidgets.QLabel('Пароль')
        self.password_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.password_add = QtWidgets.QLineEdit()
        self.password_add.setAlignment(QtCore.Qt.AlignHCenter)
        self.password_add.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button = QtWidgets.QPushButton('Войти')
        self.register_button = QtWidgets.QPushButton('У меня нет аккаунта')
        
        # Лэйаут
        self.form_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout.addWidget(self.header)
        self.form_layout.addWidget(self.login_label)
        self.form_layout.addWidget(self.login_add)
        self.form_layout.addWidget(self.password_label)
        self.form_layout.addWidget(self.password_add)
        self.form_layout.addWidget(self.login_button)
        self.form_layout.addWidget(self.register_button)

class SignInHeader (QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Авторизация')
        self.setAlignment(QtCore.Qt.AlignCenter)

class Register(QtWidgets.QWidget):
    """
    Окно регистрации пользователя
    """
    def __init__ (self, parent = None):
        super().__init__()
        self.setWindowTitle('Регистрация')
        
        # Объекты
        self.header = RegisterHeader()
        labels = ('Логин',
                  'Пароль',
                  'Повтор пароля')
        self.labels_widgets = tuple(QtWidgets.QLabel(label)
                                    for label in labels)
        self.login_add = QtWidgets.QLineEdit()
        self.password_add = QtWidgets.QLineEdit()
        self.password_add.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_confirm = QtWidgets.QLineEdit()
        self.password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_button = QtWidgets.QPushButton('Отправить запрос')
        
        # Обработчики
        self.register_button.clicked.connect(self.register)
        
        # Лэйаут
        self.form_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout.addWidget(self.header, 50)
        self.form_layout.addStretch(25)
        for label, line_adit in zip(self.labels_widgets,
                                   (self.login_add, self.password_add,
                                    self.password_confirm)):
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(label, 0)
            layout.addWidget(line_adit, 100)
            self.form_layout.addLayout(layout)
            self.form_layout.addStretch(50)
        self.form_layout.addWidget(self.register_button)
        
        # Подгон лэйблов формы под один размер
        self.equal_label_size()
    
    def equal_label_size(self):
        self.show()
        widths = tuple(label.width() for label in self.labels_widgets)
        self.hide()
        max_width = max(widths)
        for label in self.labels_widgets:
            label.setMinimumWidth(max_width)
    
    def register(self):
        def is_pass_empty(p):
            if p.replace(' ', '') == '':
                return True
        
        pass_one = self.password_add.text()
        pass_two = self.password_confirm.text()
        if pass_one != pass_two or any([is_pass_empty(p) for p in (pass_one,
                                                                   pass_two)]):
            self.password_error = RegisterPasswordError(parent = self)
            self.password_error.show()

class RegisterHeader(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Регистрация')
        self.setAlignment(QtCore.Qt.AlignCenter)

class RegisterPasswordError(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle('Разные пароли')
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        # Объекты
        self.label = QtWidgets.QLabel('Пароли не совпадают, введите заново')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Лэйаут
        self.error_layout = QtWidgets.QVBoxLayout(self)
        self.error_layout.addWidget(self.label,
                                    alignment = QtCore.Qt.AlignCenter)

class AccountWindow(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle('Мониторинг температруы')
        
        # Объекты
        self.adding_header = AddingTemperatureLabel()
        self.current_moment = mbd.current_time()
        
        self.current_datetime = QtWidgets.QLabel(self.current_moment[0],
                                                 alignment = QtCore.Qt.AlignCenter)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh_time)
        self.timer.start()
        self.temperature_label = QtWidgets.QLabel('Введите текущую температуру')
        self.temperature_add = QtWidgets.QDoubleSpinBox()
        self.temperature_add.setValue(36.6)
        self.temperature_add.setRange(35.0, 42.0)
        self.temperature_add.setSingleStep(0.1)
        self.temperature_add.setSuffix('°')
        self.temperature_add.setDecimals(1)
        self.send_temperature_button = QtWidgets.QPushButton('Оправить')
        
        # Лэйаут
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.adding_header, 50)
        self.main_layout.addWidget(self.current_datetime, 50)
        self.temperature_add_layout = QtWidgets.QHBoxLayout()
        self.temperature_add_layout.addWidget(self.temperature_label, 0)
        self.temperature_add_layout.addWidget(self.temperature_add, 100)
        self.main_layout.addStretch(25)
        self.main_layout.addLayout(self.temperature_add_layout)
        self.main_layout.addStretch(25)
        self.main_layout.addWidget(self.send_temperature_button)
        self.main_layout.addStretch(25)
    
    def refresh_time(self):
        self.current_moment = mbd.current_time()
        self.current_datetime.setText(self.current_moment[0])

class AddingTemperatureLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Запись текущей температуры')
        self.setAlignment(QtCore.Qt.AlignCenter)

class StatisticsLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Сатистика по температуре')
        self.setAlignment(QtCore.Qt.AlignCenter)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AccountWindow()
    window.show()
    sys.exit(app.exec_())