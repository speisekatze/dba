import sqlite3

queries = {
    'umgebungen': "SELECT conf_value,umgebungs_name FROM lde_conf c \
LEFT JOIN umgebung u ON (c.ind_umgebung = u.ind_umgebung) \
WHERE conf_int_name = 'tablespace' AND c.ind_umgebung IN \
    (select ind_umgebung from lde_conf WHERE conf_int_name = 'tmp_db_host' \
        AND UPPER(conf_value) = UPPER(?))"
}


def create(file):
    connection = None
    try:
        connection = sqlite3.connect(file)
        connection.text_factory = bytes
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
