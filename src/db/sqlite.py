import sqlite3

queries = {
    'umgebungen': "SELECT conf_value,umgebungs_name, c.ind_umgebung AS uid FROM lde_conf c \
LEFT JOIN umgebung u ON (c.ind_umgebung = u.ind_umgebung) \
WHERE conf_int_name = 'tablespace' AND c.ind_umgebung IN \
    (select ind_umgebung from lde_conf WHERE conf_int_name = 'tmp_db_host' \
        AND UPPER(conf_value) = UPPER(?))",
    'copy': "INSERT INTO lde_conf (conf_int_name, conf_value, conf_description, type, ind_umgebung) \
SELECT conf_int_name, conf_value, conf_description, type, ? \
FROM lde_conf WHERE ind_umgebung=?", 
    'remove': "DELETE FROM lde_conf WHERE ind_umgebung=?",
}


def create(file):
    connection = None
    try:
        connection = sqlite3.connect(file)
        connection.text_factory = bytes
    except Exception as ex:
        print(ex)
    return connection


def query(connection, query_name, param=None, commit=False):
    result = None
    sql = queries[query_name]
    cursor = connection.cursor()
    cursor.execute(sql, param)
    if cursor:
        result = cursor.fetchall()
    if commit:
        connection.commit()
    cursor.close()
    return result


def write_data_single(connection, table, data):    
    id = 0
    sSQL = 'INSERT INTO ' + table + '('+ ', '.join([x for x in data]) +') VALUES('+ ', '.join(['?' for x in data]) +');'
    try:
        write_cursor = connection.cursor()
        write_cursor.execute(sSQL, [data[x] for x in data])
    except sqlite3.Error as err:
        print("Something went wrong: {}".format(err))
    connection.commit()
    id = write_cursor.lastrowid
    write_cursor.close()
    return id

def update(connection, table, id, data):
    sSQL = 'UPDATE ' + table + ' SET ' + ', '.join([x + ' = ?' for x in data]) + ' WHERE ' + ' AND '.join([x + ' = \'' + str(id[x]) +'\'' for x in id])
    try:
        write_cursor = connection.cursor()
        write_cursor.execute(sSQL, [data[x] for x in data])
    except sqlite3.Error as err:
        print("Something went wrong: {}".format(err))
    connection.commit()
    id = write_cursor.lastrowid
    write_cursor.close()
    return id
