import pyodbc

queries = {
    'db_list_size': "SELECT \
    DB_NAME(db.database_id) DatabaseName, \
    ROUND((CAST(mfrows.RowSize AS FLOAT)*8)/1024,2) RowSizeMB, \
    ROUND((CAST(mflog.LogSize AS FLOAT)*8)/1024,2) LogSizeMB, \
    ROUND((CAST((mfrows.RowSize+mflog.LogSize) AS FLOAT)*8)/1024,2) Gesamt, \
    recovery_model_desc \
FROM sys.databases db \
    LEFT JOIN (SELECT database_id, SUM(size) RowSize \
                 FROM sys.master_files \
                WHERE type = 0 \
                GROUP BY database_id, type) mfrows ON mfrows.database_id = db.database_id \
    LEFT JOIN (SELECT database_id, SUM(size) LogSize \
                 FROM sys.master_files \
                WHERE type = 1 \
                GROUP BY database_id, type) mflog ON mflog.database_id = db.database_id \
    WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') ORDER BY DB_NAME(db.database_id);",
    'simple': 'ALTER DATABASE {0} SET RECOVERY SIMPLE;',
    'shrink': "DBCC SHRINKDATABASE (?, NOTRUNCATE);"
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
        connection = pyodbc.connect(connection_string, autocommit=True)
    except Exception as ex:
        print(ex)
    return connection


def load_table(connection, table, where='', fields='*'):
    print('load')
    query = None
    result = None
    sql = 'SELECT '+fields+' FROM ' + table
    if where != '':
        sql += ' WHERE ' + where
    load_cursor = connection.cursor()
    query = load_cursor.execute(sql)
    if query:
        result = query.fetchall()
    load_cursor.close()
    connection.commit()
    return result


def find_in_table(connection, table, where, data):
    print('find')
    sql = 'SELECT * FROM '+table+' WHERE '+where
    find_cursor = connection.cursor()
    result = find_cursor.execute(sql, data).fetchall()
    find_cursor.close()
    connection.commit()
    return result


def query(connection, query_name, param=None):
    result = None
    sql = queries[query_name]
    cursor = connection.cursor()
    if param is not None:
        query = cursor.execute(sql, param)
    else:
        query = cursor.execute(sql)
    if query:
        result = query.fetchall()
    cursor.close()
    connection.commit()
    return result


def query_format(connection, query_name, param):
    result = None
    sql = queries[query_name]
    cursor = connection.cursor()
    s = sql.format(param)
    print(s)
    cursor.execute(s)
    cursor.close()
    connection.commit()
    return result
