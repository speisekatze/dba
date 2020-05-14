import pyodbc

queries = {
    'db_list_size': "SELECT \
    DB_NAME(db.database_id) DatabaseName, \
    (CAST(mfrows.RowSize AS FLOAT)*8)/1024 RowSizeMB, \
    (CAST(mflog.LogSize AS FLOAT)*8)/1024 LogSizeMB \
FROM sys.databases db \
    LEFT JOIN (SELECT database_id, SUM(size) RowSize \
                 FROM sys.master_files \
                WHERE type = 0 \
                GROUP BY database_id, type) mfrows ON mfrows.database_id = db.database_id \
    LEFT JOIN (SELECT database_id, SUM(size) LogSize \
                 FROM sys.master_files \
                WHERE type = 1 \
                GROUP BY database_id, type) mflog ON mflog.database_id = db.database_id \
    WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb');"
}


def build_connection_string(config):
    c_string = 'DRIVER={SQL Server};'
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


def query(connection, query_name):
    result = None
    sSQL = queries[query_name]
    cursor = connection.cursor()
    query = cursor.execute(sSQL)
    if query:
        result = query.fetchall()
    cursor.close()
    return result
