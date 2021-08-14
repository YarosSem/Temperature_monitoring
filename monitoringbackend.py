import datetime
import mysql.connector
from mysql.connector import Error, MySQLConnection
import hashlib
import re
import numpy as np

def current_time():
    """"
    Возвращает строку с текущей датой и временем
    """
    now = datetime.datetime.now()
    date = now.date()
    day = date.day
    mounth = date.month
    year = date.year
    time = now.time()
    hours = time.hour
    minutes = time.minute
    seconds = time.second
    
    result_row = '{day:0>2d}.{mounth:0>2d}.{year:0>4d} {hour:0>2d}:{minute:0>2d}:{second:0>2d}'.format(day = day,
                                                                         mounth = mounth,
                                                                         year = year,
                                                                         hour = hours,
                                                                         minute = minutes,
                                                                         second = seconds)
    return result_row, str(date), str(time)[0 : str(time).index('.')]

def connection_to_base(host = 'localhost',
                       database = 'temperature_monitoring',
                       user = 'root',
                       password = '12345678'):
    """
    Проверка подключения к базе
    В случае подключения возвращает словарь с аргументами функции
    """
    try:
        conn = mysql.connector.connect(host = host,
                                       database = database,
                                       user = user,
                                       password = password)
        if conn.is_connected():
            res = dict(host = host, database = database,
                       user = user, password = password)
        conn.close()
    except Error:
        res = False
    
    return res

def autorisation(login, password, dbconfig):
    """
    Проверяет соответствие логина и пароля в базе
    В случае совпадения возвращает id плоьзователя
    В случае несовпадения возвращает False
    """
    
    def check_password(login_id, password, cursor):
        """
        Проверяет совпадение password и пароля из базы
        Возвращает True, если совпадение обнаружено
        """
        password_query = """
                         SELECT pass
                         FROM login
                         WHERE login_id = "{login_id}"
                         """.format(login_id = login_id)
        cursor.execute(password_query)
        row = cursor.fetchall()
        
        hasher = hashlib.md5()
        hasher.update(password.encode('utf-8'))
        hashed_password = str(hasher.digest())[2 : -1].replace('\\', '')
        if row and row[0][0] == hashed_password:
            return True
        else:
            return False
    
    if not password_is_correct(password):
        return False
    
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    # Проверка налиция логина в базе
    login_id = get_login_id(login, cursor)
    if not login_id:
        conn.close()
        return False
    # Проверка на совпадение паролей
    if not check_password(login_id, password, cursor):
        conn.close()
        return False
    else:
        conn.close()
        return login_id

def get_login_id(login, cursor):
        """"
        Выбирает login_id из базы
        В случае несовпадения возвращает False
        """
        login_id_query = """
                         SELECT login_id
                         FROM login
                         WHERE login_name = "{login}";
                         """.format(login = login)
        #print(login_id_query)
        cursor.execute(login_id_query)
        row = cursor.fetchall()
        if row:
            return row[0][0]
        else:
            return False

def registration(login, password, dbconfig):
    """
    Производит регистрацию пользователя
    Возвращает True, если данные в базу успешно внесены
    """
    
    def login_is_correct(login):
        """
        Возвращает True, если логин состоит из допустимых символов
        """
        match = re.match('^[a-zA-Z0-9_!@#$%^&*()]+$', login)
        if match:
            return True
        else:
            return False
    
    # Проверка корректности введенных логина и пароля
    if not login_is_correct(login) or not password_is_correct(password):
        return False
    
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    #Проверка наличия пользователя с таким же логином
    if get_login_id(login, cursor):
        conn.close()
        return False
    hasher = hashlib.md5()
    hasher.update(password.encode('utf-8'))
    hashed_password = str(hasher.digest())[2 : -1].replace('\\', '')
    # Дополнение таблицы login
    insertion_query = """
                      INSERT INTO login (login_name, pass)
                      VALUES ('{login}', '{password}');
                      """.format(login = login, password = hashed_password)
    cursor.execute(insertion_query)
    conn.commit()
    conn.close()
    return True

def password_is_correct(password):
        """
        Возвращает True, если логин состоит из допустимых символов
        """
        match = re.match('^[a-zA-Z0-9_!@#$%^&*()]+$', password)
        if match:
            return True
        else:
            return False

def current_sickness_figure_points(login_id, dbconfig):
    """
    Возвращает:
        -координаты точек для графика по текущей болезни
        -координаты дневных делителей по оси абсцисс
        -координаты дневных делителей по оси ординат
    """
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    
    # Запрос на данные о болезнях пользователя за последние 30 дней
    query = """
            SELECT temperature, measurement_day, measurement_time
            FROM temperature_measurement
            WHERE login_id = {login_id} AND DATEDIFF(CURRENT_DATE, measurement_day) < 30
            ORDER BY measurement_day ASC, measurement_time DESC;
            """.format(login_id = login_id)
    cursor.execute(query)
    rows = cursor.fetchall()
    # Если запрос ничего не вернул
    if not rows:
        conn.close()
        return None
    
    # Заполненние списака, включающего записи по текущей болезни
    current_sickness_list = []
    now = datetime.datetime.now()
    now_date = now.date()
    if (now_date - rows[-1][1]).days >= 7:  # Если последняя запись была не
        conn.close()                        # менее недели назад
        return None
    current_sickness_list.append(rows[-1])
    for row in rows[::-1][1:]:
        if (current_sickness_list[-1][1] - row[1]).days < 6:
            current_sickness_list.append(row)
        else:
            break
    # Заполнение списка из кортежей, включающих записи дня
    monitoring_days = tuple(set(row[1] for row in current_sickness_list))
    #print(monitoring_days)
    current_sickness_list_days = []
    index = 0
    len_csld = len(current_sickness_list)
    for day in monitoring_days:
        current_sickness_list_days.append([])
        for i in range(index, len_csld):
            row = current_sickness_list[i]
            if row[1] == day:
                current_sickness_list_days[-1].append(row)
            else:
                index = i
                break
    #print(current_sickness_list_days)
    
    # Определение координат точек
    # Координаты дневных делений по оси асбсцисс
    x_days_points = np.linspace(0, 1000, len(monitoring_days) + 1)
    # Координаты точек измерения температуры
    temperature_coords = np.array([[0, 0]])[:-1] # Пустой двумерный массив
    for i, day in enumerate(current_sickness_list_days[::-1]):
        day_x_coords = x_days_points[i : i + 2]
        for row in day:
            x = day_x_coords[0] + (day_x_coords[1] -day_x_coords[0]) * row[2].seconds / 86400
            y = float(row[0])
            temperature_coords = np.vstack((temperature_coords, [x, y]))
    #print(temperature_coords)
    # Координаты дневных делений по оси ординат
    y_days_points = np.array([temperature_coords[:, 1].min(), temperature_coords[:, 1].max()])
    conn.close()
    #print(x_days_points[1 : -1])
    #print(y_days_points)
    return temperature_coords, x_days_points[ 1: -1], y_days_points

def insert_temperature_mesurement_result(temperature, measurement_day,
                                         measurement_time, login_id, dbconfig):
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    
    insertion_query = """
                      INSERT INTO temperature_measurement (login_id, temperature,
                                                           measurement_day, measurement_time)
                      VALUES ({login_id}, {temperature}, '{measurement_day}', '{measurement_time}');
                      """.format(login_id = login_id, temperature = temperature,
                                 measurement_day = measurement_day,
                                 measurement_time = measurement_time)
    cursor.execute(insertion_query)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    current_sickness_figure_points(3, connection_to_base())
