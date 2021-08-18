# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:13:27 2021

@author: yaros
"""

from PyQt5 import QtWidgets
from PyQt5 import QtCore
import PyQt5.QtGui as QtGui
import sys
import monitoringbackend as mbd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Табилца стилей
css = open('./stylesheet.css').read()

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(css)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        self.dbconfig = mbd.connection_to_base()
        if self.dbconfig:
            self.autorisation_process()
        else:
            self.database_setting_process()
    
    def database_setting_process(self):
        self.database_setting = DatabaseSetting()
        self.main_layout.addWidget(self.database_setting)
        
        # Обработчик
        self.database_setting.confirm_button.clicked.connect(self.database_setting_try)
    
    def database_setting_try(self):
        host = self.database_setting.host_edit.text()
        database = self.database_setting.database_edit.text()
        user = self.database_setting.user_edit.text()
        password = self.database_setting.password_edit.text()
        self.dbconfig = mbd.connection_to_base(host = host,
                                               database = database,
                                               user = user,
                                               password = password)
        if self.dbconfig:
            self.main_layout.removeWidget(self.database_setting)
            self.database_setting.deleteLater()
            self.autorisation_process()
        else:
            self.database_setting_error = DatabaseSettingError(parent = self)
            self.database_setting_error.show()
    
    def autorisation_process(self):
        self.sign_in = SignIn(parent = self)
        self.main_layout.addWidget(self.sign_in)
        
        # Обработчики
        self.sign_in.login_button.clicked.connect(self.autorisation_try)
        self.sign_in.register_button.clicked.connect(self.registration_process)
    
    def autorisation_try(self):
        login = self.sign_in.login_add.text()
        password = self.sign_in.password_add.text()
        res = mbd.autorisation(login, password, self.dbconfig)
        if res:
            self.login_id = res
            self.account_window = AccountWindow(self.login_id, self.dbconfig)
            self.main_layout.removeWidget(self.sign_in)
            self.main_layout.addWidget(self.account_window)
            self.sign_in.deleteLater()
        else:
            error = AutorisationError(parent = self)
            error.show()
    
    def registration_process(self):
        self.register = Register()
        self.main_layout.removeWidget(self.sign_in)
        self.main_layout.addWidget(self.register)
        self.sign_in.deleteLater()
        
        # Обработчик
        self.register.register_button.clicked.connect(self.registration_try)
    
    def registration_try(self):
        if self.register.ready == True:
            login = self.register.login_add.text()
            password = self.register.password_confirm.text()
            registration = mbd.registration(login, password, self.dbconfig)
            if registration:
                self.main_layout.removeWidget(self.register)
                self.register.deleteLater()
                self.autorisation_process()
            else:
                error = RegistrationError(parent = self)
                error.show()

class HeaderFont(QtGui.QFont):
    """
    Шрифт для заголовков
    """
    def __init__(self):
        super().__init__('Calibri')
        self.setPointSize(20)
        self.setBold(True)

class LabelsFont(QtGui.QFont):
    """
    Шрифт для надписей к формам, кнопкам и сообщениям об ошибке
    """
    def __init__(self):
        super().__init__('Calibri')
        self.setPointSize(14)

class EditFont(QtGui.QFont):
    """
    Шрифт для QLineEdit
    """
    def __init__(self):
        super().__init__('Calibri')
        self.setPointSize(12)

class DatabaseSetting(QtWidgets.QWidget):
    """
    Окно настройки подключения к базе
    """
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle('Настройка подключения')
        self.setMaximumHeight(400)
        
        # Объекты
        self.head_label = QtWidgets.QLabel('Введите параметры подключения')
        self.head_label.setObjectName('setting_header')
        self.head_label.setFont(HeaderFont())
        self.head_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.host_label = QtWidgets.QLabel('Адрес хоста:')
        self.host_label.setFont(LabelsFont())
        self.host_edit = QtWidgets.QLineEdit()
        self.host_edit.setFont(EditFont())
        self.database_label = QtWidgets.QLabel('Название базы:')
        self.database_label.setFont(LabelsFont())
        self.database_edit = QtWidgets.QLineEdit()
        self.database_edit.setFont(EditFont())
        self.user_label = QtWidgets.QLabel('Имя пользователя:')
        self.user_label.setFont(LabelsFont())
        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setFont(EditFont())
        self.password_label = QtWidgets.QLabel('Пароль:')
        self.password_label.setFont(LabelsFont())
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setFont(EditFont())
        self.confirm_button = QtWidgets.QPushButton('Применить')
        self.confirm_button.setFont(LabelsFont())
        
        # Лэйаут
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout = QtWidgets.QGridLayout()
        self.form_layout.addWidget(self.host_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.database_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.user_label, 2, 0, 1, 1)
        self.form_layout.addWidget(self.password_label, 3, 0, 1, 1)
        self.form_layout.addWidget(self.host_edit, 0, 1, 1, 3)
        self.form_layout.addWidget(self.database_edit, 1, 1, 1, 3)
        self.form_layout.addWidget(self.user_edit, 2, 1, 1, 3)
        self.form_layout.addWidget(self.password_edit, 3, 1, 1, 3)
        self.main_layout.addWidget(self.head_label)
        self.main_layout.addSpacing(25)
        self.main_layout.addStretch(100)
        self.main_layout.addLayout(self.form_layout, stretch=100)
        self.main_layout.addSpacing(25)
        self.main_layout.addStretch(100)
        self.main_layout.addWidget(self.confirm_button)

class DatabaseSettingError(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle('Ошибка настройки подключения')
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        # Объекты
        self.label = QtWidgets.QLabel('Введены неверные параметры для подключения')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(LabelsFont())
        
        # Лэйаут
        self.error_layout = QtWidgets.QVBoxLayout(self)
        self.error_layout.addWidget(self.label,
                                    alignment = QtCore.Qt.AlignCenter)

class AutorisationError(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle('Ошибка авторизации')
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        # Объекты
        self.label = QtWidgets.QLabel('Неправильно введен логин или пароль')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(LabelsFont())
        
        # Лэйаут
        self.error_layout = QtWidgets.QVBoxLayout(self)
        self.error_layout.addWidget(self.label,
                                    alignment = QtCore.Qt.AlignCenter)

class RegistrationError(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setWindowTitle('Ошибка регистрации')
        self.setMinimumWidth(300)
        self.setMinimumHeight(100)
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        # Объекты
        self.label = QtWidgets.QLabel('В поля введены недопустимые значения')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(LabelsFont())
        
        # Лэйаут
        self.error_layout = QtWidgets.QVBoxLayout(self)
        self.error_layout.addWidget(self.label,
                                    alignment = QtCore.Qt.AlignCenter)

class SignIn(QtWidgets.QWidget):
    """"
    Окно авторизации
    """
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setMaximumHeight(400)
        self.setMinimumWidth(300)
        
        # Объекты
        self.header = SignInHeader()
        self.login_label = QtWidgets.QLabel('Логин')
        self.login_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.login_label.setFont(LabelsFont())
        self.login_add = QtWidgets.QLineEdit()
        self.login_add.setAlignment(QtCore.Qt.AlignHCenter)
        self.login_add.setFont(EditFont())
        self.password_label = QtWidgets.QLabel('Пароль')
        self.password_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.password_label.setFont(LabelsFont())
        self.password_add = QtWidgets.QLineEdit()
        self.password_add.setAlignment(QtCore.Qt.AlignHCenter)
        self.password_add.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_add.setFont(EditFont())
        self.login_button = QtWidgets.QPushButton('Войти')
        self.login_button.setFont(LabelsFont())
        self.register_button = QtWidgets.QPushButton('У меня нет аккаунта')
        self.register_button.setFont(LabelsFont())
        
        # Лэйаут
        self.form_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout.addStretch(1)
        self.form_layout.addWidget(self.header, alignment = QtCore.Qt.AlignVCenter)
        self.form_layout.addSpacing(25)
        self.form_layout.addStretch(1)
        self.form_layout.addWidget(self.login_label, alignment = QtCore.Qt.AlignVCenter,
                                   stretch = 1)
        self.form_layout.addWidget(self.login_add, stretch = 1)
        self.form_layout.addWidget(self.password_label, alignment = QtCore.Qt.AlignVCenter,
                                   stretch = 1)
        self.form_layout.addWidget(self.password_add)
        self.form_layout.addStretch(1)
        self.form_layout.addSpacing(25)
        self.form_layout.addWidget(self.login_button, stretch = 1)
        self.form_layout.addWidget(self.register_button, stretch = 1)
        self.form_layout.addStretch(1)

class SignInHeader (QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Авторизация')
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(HeaderFont())

class Register(QtWidgets.QWidget):
    """
    Окно регистрации пользователя
    """
    def __init__ (self, parent = None):
        super().__init__()
        self.setWindowTitle('Регистрация')
        self.setMinimumWidth(400)
        self.ready = False
        
        # Объекты
        self.header = RegisterHeader()
        labels = ('Логин:',
                  'Пароль:',
                  'Повтор пароля:')
        self.labels_widgets = tuple(QtWidgets.QLabel(label)
                                    for label in labels)
        for label in self.labels_widgets:
            label.setFont(LabelsFont())
        self.login_add = QtWidgets.QLineEdit()
        self.login_add.setFont(EditFont())
        self.password_add = QtWidgets.QLineEdit()
        self.password_add.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_add.setFont(EditFont())
        self.password_confirm = QtWidgets.QLineEdit()
        self.password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_confirm.setFont(EditFont())
        self.register_button = QtWidgets.QPushButton('Отправить запрос')
        self.register_button.setFont(LabelsFont())
        
        # Обработчики
        self.register_button.clicked.connect(self.register)
        
        # Лэйаут
        self.form_layout = QtWidgets.QVBoxLayout(self)
        self.form_layout.addStretch(50)
        self.form_layout.addWidget(self.header, 50)
        self.form_layout.addSpacing(25)
        self.form_layout.addStretch(50)
        for label, line_adit in zip(self.labels_widgets,
                                   (self.login_add, self.password_add,
                                    self.password_confirm)):
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(label, 0)
            layout.addWidget(line_adit, 100)
            self.form_layout.addLayout(layout)
            self.form_layout.addStretch(20)
        self.form_layout.addSpacing(25)
        self.form_layout.addStretch(50)
        self.form_layout.addWidget(self.register_button)
        self.form_layout.addStretch(50)
        
        # Подгон лэйблов формы под один размер
        self.equal_label_size()
    
    def equal_label_size(self):
        widths = tuple(150 for label in self.labels_widgets)
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
            self.ready = False
        else:
            self.ready = True

class RegisterHeader(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Регистрация')
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(HeaderFont())

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
        self.label.setFont(LabelsFont())
        
        # Лэйаут
        self.error_layout = QtWidgets.QVBoxLayout(self)
        self.error_layout.addWidget(self.label,
                                    alignment = QtCore.Qt.AlignCenter)

class AccountWindow(QtWidgets.QWidget):
    """
    Окно пользователя
    """
    def __init__(self, login_id, dbconfig, parent = None):
        super().__init__()
        self.setWindowTitle('Мониторинг температруы')
        self.setMinimumWidth(800)
        self.setMinimumHeight(650)
        
        # Объекты
        self.adding_header = AddingTemperatureLabel()
        self.current_moment = mbd.current_time()
        self.login_id = login_id
        self.dbconfig = dbconfig
        
        self.current_datetime = QtWidgets.QLabel(self.current_moment[0],
                                                 alignment = QtCore.Qt.AlignCenter)
        self.current_datetime.setFont(LabelsFont())
        self.current_datetime.setObjectName('current_time')
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.refresh_time)
        self.timer.start()
        self.temperature_label = QtWidgets.QLabel('Введите текущую температуру:')
        self.temperature_label.setFont(LabelsFont())
        self.temperature_add = QtWidgets.QDoubleSpinBox()
        self.temperature_add.setValue(36.6)
        self.temperature_add.setRange(35.0, 42.0)
        self.temperature_add.setSingleStep(0.1)
        self.temperature_add.setSuffix('°')
        self.temperature_add.setDecimals(1)
        self.temperature_add.setFont(EditFont())
        self.send_temperature_button = QtWidgets.QPushButton('Оправить')
        self.send_temperature_button.setFont(LabelsFont())
        self.send_temperature_button.setMinimumHeight(50)
        self.figure_widget = PlotCanvas(mbd.current_sickness_figure_points(login_id, dbconfig))
        
        # Обработчики
        self.send_temperature_button.clicked.connect(self.send_temperature)
        
        # Лэйаут
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.adding_header, 50)
        #self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.current_datetime, 50)
        #self.main_layout.addSpacing(5)
        self.temperature_add_layout = QtWidgets.QHBoxLayout()
        self.temperature_add_layout.addWidget(self.temperature_label, 0)
        self.temperature_add_layout.addSpacing(10)
        self.temperature_add_layout.addWidget(self.temperature_add, 100)
        #self.main_layout.addStretch(5)
        self.main_layout.addLayout(self.temperature_add_layout)
        #self.main_layout.addStretch(25)
        self.main_layout.addWidget(self.send_temperature_button)
        self.main_layout.addSpacing(25)
        #self.main_layout.addStretch(25)
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
        self.setFont(HeaderFont())

class StatisticsLabel(QtWidgets.QLabel):
    def __init__(self, parent = None):
        super().__init__('Сатистика по температуре')
        self.setAlignment(QtCore.Qt.AlignCenter)

class PlotCanvas(FigureCanvas):
    """
    Виджет графика
    """
    def __init__(self, data, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('#00cf91')
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
                   s = 50)
        for x in x_days_points:
            ax.plot([x, x], y_days_points, color = 'lightblue',
                    ls = '--', lw = '0.8')
        ax.set_title('Результаты термометрии по текущей болезни', pad = 20,
                     fontsize = 16, fontdict = {'family' : 'calibri'})
        ax.set_ylabel('Температура [°С]', labelpad = 15, fontsize = 14, family = 'calibri')
        ax.set_xlabel('Период болезни', labelpad = 12, fontsize = 14, family = 'calibri')
        ax.set_xlim(left = 0, right = 1000)
        ax.set_ylim(top = y_days_points[1], bottom = y_days_points[0])
        ax.grid(True, axis = 'y', ls = ':')
        ax.set_xticks([])
        self.draw()
    
    def message(self):
        ax = self.fig.add_subplot(111)
        ax.text(0.27, 0.45, 'Данных пока нет', size = 20, color = 'red')
        self.draw()

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    #window = AccountWindow(3, mbd.connection_to_base())
    window = App()
    #window = DatabaseSetting()
    #window = Register()
    #window = AutorisationError()
    window.show()
    sys.exit(app.exec_())