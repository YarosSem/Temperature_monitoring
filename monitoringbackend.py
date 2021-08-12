import datetime
import mysql.connector
from mysql.connector import Error, MySQLConnection
import hashlib
import re

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
    
    result_row = '{day}.{mounth}.{year} {hour}:{minute}:{second}'.format(day = day,
                                                                         mounth = mounth,
                                                                         year = year,
                                                                         hour = hours,
                                                                         minute = minutes,
                                                                         second = seconds)
    return result_row

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
