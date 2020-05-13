import pyodbc


def build_connection_string(config):
    c_string = ''
    if config['driver'] == 'MSSQL':
        c_string += 'DRIVER={SQL Server};'
    else:
        raise Exception('Kein Treiber angegeben oder Treiber nicht verfügbar')
    c_string += 'SERVER=' + config['server'] + '\\' + config['instance'] + ';'
    c_string += 'UID=' + config['user'] + ';'
    c_string += 'PWD=' + config['password'] + ';'
    c_string += 'DATABASE=model'
    return c_string


def create(config):
    connection = None
    try:
        connection_string = build_connection_string(config)
        connection = pyodbc.connect(connection_string)
    except Exception as ex:
        print(ex)
    return connection


def load_table(connection, table, where='', fields='*'):
    query = None
    result = None
    sSQL = 'SELECT '+fields+' FROM ' + table
    if where != '':
        sSQL += ' WHERE ' + where
    # sSQL += ";"
    load_cursor = connection.cursor()
    query = load_cursor.execute(sSQL)
    if query:
        result = query.fetchall()
    load_cursor.close()
    return result


def find_in_table(connection, table, where, data):
    sSQL = 'SELECT * FROM '+table+' WHERE '+where
    # print(sSQL)
    # print(data)
    # print('------')
    find_cursor = connection.cursor()
    result = find_cursor.execute(sSQL, data).fetchall()
    find_cursor.close()
    return result
