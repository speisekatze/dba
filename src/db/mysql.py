import mysql.connector


queries = {
    'db_list_size': "SELECT table_schema AS NAME, \
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size, \
        0 AS LogSize, \
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS gesamt, \
        ENGINE AS info \
FROM information_schema.tables \
WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'test', 'mysql') \
GROUP BY table_schema ORDER BY table_schema;",
    'find_db_dbt': "SELECT geplante_vern_am, ziel_db FROM Datenbank WHERE vernichtet_db = 0 \
        AND ziel_db LIKE %s ORDER BY bereitgestellt_am DESC LIMIT 1;",
    'db_dbt_all': "SELECT geplante_vern_am, ziel_db, datenbank_id FROM Datenbank",
    'get_kunden': "SELECT * FROM Kunde",
}


def create(config):
    connection = None
    try:
        connection = mysql.connector.connect(user=config['user'],
                                             password=config['password'],
                                             host=config['server'],
                                             database=config['database'])
    except Exception as ex:
        print(ex)
    return connection


def query(connection, query_name, param=None):
    result = None
    sql = queries[query_name]
    cursor = connection.cursor()
    cursor.execute(sql, param)
    if cursor:
        result = cursor.fetchall()
    cursor.close()
    return result


def drop(connection, db_name):
    sql_drop = "DROP DATABASE {0}"
    cursor = connection.cursor()

    s = sql_drop.format(db_name)
    cursor.execute(s)

    cursor.close()
    connection.commit()
    return None

def write_data_single(connection, table, data):
    id = 0
    sSQL = 'INSERT INTO ' + table + '('+ ', '.join([x for x in data]) +') VALUES('+ ', '.join(['%s' for x in data]) +');'
    try:
        write_cursor = connection.cursor()
        write_cursor.execute(sSQL, [data[x] for x in data])
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
    connection.commit()
    id = write_cursor.lastrowid
    write_cursor.close()
    return id