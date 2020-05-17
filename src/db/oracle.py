import cx_Oracle

queries = {
    'db_list_size': "SELECT DISTINCT owner || '/' || a.tablespace_name, \
                                     ROUND(a.bytes/1024/1024,2) AS sze, \
                                     ROUND(c.bytes/1024/1024,2) AS tmp_size, \
                                     ROUND((a.bytes+c.bytes)/1024/1024,2) AS tmp_size, \
                                     ROUND(b.bytes/1024/1024,2) AS free \
FROM (select default_tablespace, temporary_tablespace FROM dba_users \
    WHERE default_tablespace NOT IN ('USERS', 'SYSTEM', 'SYSAUX')) tbls \
LEFT JOIN (select owner, tablespace_name, sum(bytes) AS bytes from dba_segments \
    WHERE tablespace_name NOT IN ('SYSTEM', 'SYSAUX') AND owner NOT IN ('SYS') \
        GROUP BY OWNER,tablespace_name ) a ON (tbls.default_tablespace = a.tablespace_name) \
LEFT JOIN (SELECT tablespace_name,SUM(bytes) AS bytes FROM DBA_free_space \
    GROUP BY tablespace_name) b ON (tbls.default_tablespace = b.tablespace_name) \
LEFT JOIN (SELECT tablespace_name, bytes FROM dba_temp_files) c \
    ON (tbls.temporary_tablespace = c.tablespace_name)",
}


def build_connection_string(config):
    # username/passwort@hostname.de.oracle.com:1521/servicename
    c_string = config['user']
    c_string += '/' + config['password']
    c_string += '@' + config['server']
    # cx_Oracle doesn't like 'port'
    c_string += '/' + config['instance']
    print(c_string)
    return c_string


def create(config):
    connection = None
    try:
        connection = cx_Oracle.connect(build_connection_string(config), mode=cx_Oracle.SYSDBA)
    except Exception as ex:
        print(ex)
    return connection


def query(connection, query_name, param=None):
    if connection is None:
        return [()]
    result = None
    sql = queries[query_name]
    cursor = connection.cursor()
    cursor.execute(sql, param)
    if cursor:
        result = cursor.fetchall()
    cursor.close()
    return result
