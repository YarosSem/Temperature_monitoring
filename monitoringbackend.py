# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 18:09:20 2021

@author: yaros
"""

import datetime
import mysql.connector
from mysql.connector import Error, MySQLConnection

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
        if row and row[0][0] == password:
            return True
        else:
            return False
    
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    # Проверка налиция логина в базе
    login_id = get_login_id(login, cursor)
    if not login_id:
        return False
    # Проверка на совпадение паролей
    if not check_password(login_id, password, cursor):
        return False
    else:
        return login_id

def limb():
    a = 2
    b = 1
    return a + b

if __name__ == '__main__':
    a = 1


