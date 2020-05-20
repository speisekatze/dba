import mysql.connector


queries = {
    'db_list_size': "SELECT table_schema AS NAME, \
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size, \
        0 AS LogSize, \
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS gesamt, \
        ENGINE AS info \
FROM information_schema.tables \
WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'test', 'mysql') \
GROUP BY table_schema;",
    'find_db_dbt': "SELECT geplante_vern_am, ziel_db FROM Datenbank WHERE vernichtet_db = 0 \
        AND ziel_db LIKE %s ORDER BY bereitgestellt_am DESC LIMIT 1;",
    'db_dbt_all': "SELECT geplante_vern_am, ziel_db FROM Datenbank",
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
