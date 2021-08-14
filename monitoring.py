# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:13:27 2021

@author: yaros
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
import sys
import monitoringbackend as mbd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
    def __init__(self, login_id, dbconfig, parent = None):
        super().__init__()
        self.setWindowTitle('Мониторинг температруы')
        
        # Объекты
        self.adding_header = AddingTemperatureLabel()
        self.current_moment = mbd.current_time()
        self.login_id = login_id
        self.dbconfig = dbconfig
        
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
        self.figure_widget = PlotCanvas(mbd.current_sickness_figure_points(login_id, dbconfig))
        
        # Обработчики
        self.send_temperature_button.clicked.connect(self.send_temperature)
        
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
        self.main_layout.addWidget(self.figure_widget)
    
    def refresh_time(self):
        self.current_moment = mbd.current_time()
        self.current_datetime.setText(self.current_moment[0])
    
    def send_temperature(self):
        temperature = self.temperature_add.value()
        mbd.insert_temperature_mesurement_result(temperature,
                                                 self.current_moment[1],
                                                 self.current_moment[2],
                                                 self.login_id,
                                                 self.dbconfig)
        self.figure_widget.draw_figure(mbd.current_sickness_figure_points(self.login_id, self.dbconfig))

class AddingTemperatureLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Запись текущей температуры')
        self.setAlignment(QtCore.Qt.AlignCenter)

class StatisticsLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Сатистика по температуре')
        self.setAlignment(QtCore.Qt.AlignCenter)

class PlotCanvas(FigureCanvas):
    def __init__(self, data, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.draw_figure(data)

    def draw_figure(self, data):
        if data:
            self.plot(data[0], data[1], data[2])
        else:
            self.message()

    def plot(self, temperature_points, x_days_points, y_days_points):
        y_reserve = 0.5
        y_days_points[0] -= y_reserve
        y_days_points[1] += y_reserve
        ax = self.fig.add_subplot(111)
        ax.plot(temperature_points[:, 0], temperature_points[:, 1], 'g-')
        ax.scatter(temperature_points[:, 0], temperature_points[:, 1], color = 'blue',
                   s = 100)
        for x in x_days_points:
            ax.plot([x, x], y_days_points, color = 'lightblue',
                    ls = '--', lw = '0.8')
        ax.set_title('Результаты термометрии по текущей болезни', pad = 15)
        ax.set_xlim(left = 0, right = 1000)
        ax.set_ylim(top = y_days_points[1], bottom = y_days_points[0])
        ax.grid(True, axis = 'y', ls = ':')
        self.draw()
    
    def message(self):
        ax = self.fig.add_subplot(111)
        ax.text(0.22, 0.45, 'Данных пока нет', size = 20)
        self.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AccountWindow(3, mbd.connection_to_base())
    window.show()
    sys.exit(app.exec_())