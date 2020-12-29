import cx_Oracle
from src.ssh import ssh

queries = {
    'db_list_size': "SELECT DISTINCT owner, \
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
    if param is not None:
        query = cursor.execute(sql, param)
    else:
        query = cursor.execute(sql)
    if query:
        result = query.fetchall()
    cursor.close()
    return result


def drop(connection, db_name):
    sql_schema = 'DROP USER {1} CASCADE;'
    cursor = connection.cursor()

    s = sql_schema.format(db_name)
    cursor.execute(s)

    cursor.close()
    connection.commit()
    return None

def import_db(connection, data):
    client = ssh('Oracle')
    client.open()
    print(data)
    sqlfile_string = '/oracle/product/12.2.0/dbhome_1/bin/impdp \\"sys/{0}@192.168.1.219:1521/orcl as sysdba\\" DIRECTORY=logodata DUMPFILE={1} SQLFILE={1}.sql'
    import_string = '/oracle/product/12.2.0/dbhome_1/bin/impdp \\"sys/{0}@192.168.1.219:1521/orcl AS SYSDBA\\" DIRECTORY=logodata DUMPFILE={1} REMAP_SCHEMA={2}:{3} REMAP_TABLESPACE={4}:{5} TABLE_EXISTS_ACTION=REPLACE LOGFILE=imp_{1}.log'
    sqlfile_command = sqlfile_string.format(client.conf['db_pass'], data['filename'])
    env_dict = {
        'ORACLE_HOME': '/oracle/product/12.2.0/dbhome_1',
        'LD_LIBRARY_PATH': '/oracle/product/12.2.0/dbhome_1/lib',
        'PATH': '/usr/lib64/qt-3.3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/oracle/.local/bin:/home/oracle/bin:/oracle/product/12.2.0/dbhome_1/bin',
        'ORACLE_BASE': '/oracle',
    }

    m, e = client.cmd(sqlfile_command, env=env_dict)
    m, e = client.cmd('grep -m 1 "TABLESPACE" /oradata/share/{0}.sql'.format(data['filename']))
    tablespace = m[0].split('"')[1]
    m, e = client.cmd('grep -m 1 "CREATE TABLE" /oradata/share/{0}.sql'.format(data['filename']))
    schema = m[0].split('"')[1]
    import_command = import_string.format(client.conf['db_pass'], data['filename'], schema, data['db_name'], tablespace, data['db_name'])
    m, e = client.cmd(import_command, env=env_dict)
    m, e = client.cmd('rm /oradata/share/{0}.sql'.format(data['filename']))
