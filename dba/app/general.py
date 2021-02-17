from src.db import mysql, sqlite
import re


def connect_dbt(conf):
    dbt_conf = {
        'user': conf['dba']['dbt']['user'],
        'password': conf['dba']['dbt']['password'],
        'server': conf['dba']['dbt']['fqdn'],
        'database': conf['dba']['dbt']['database']
    }
    return mysql.create(dbt_conf)


def load_dbt(connection):
    dbt = mysql.query(connection, 'db_dbt_all')
    return dbt


def find_in_dbt(dbt, instance, db_name):
    result = None
    pattern = None
    if instance is None:
        pattern = re.compile(r'\w - ' + db_name + '$', re.I)
    else:
        pattern = re.compile(instance + ' - ' + db_name + '$', re.I)
    for db in dbt:
        if pattern.search(db[1]):
            result = db
    return result


def prepare_config(configuration, host, instance=None):
    conf = {}
    for item in configuration['dba']['database']['hosts']:
        if item['name'] == host:
            conf['server'] = item['fqdn']
            conf['driver'] = item['driver']
            if 'lde_conf' in item:
                conf['lde_conf'] = item['lde_conf']
            conf['database'] = ''
            if instance is not None:
                conf['instance'] = prepare_instance_config(item, instance)
            conf['user'] = item['user']
            conf['password'] = item['password']
            if 'instance' in conf and conf['instance'] is not None:
                if 'user' in conf['instance'] and 'password' in conf['instance']:
                    conf['user'] = conf['instance']['user']
                    conf['password'] = conf['instance']['password']
                conf['instance'] = conf['instance']['name']
    return conf


def prepare_instance_config(item, instance):
    conf = None
    if 'instances' in item:
        for inst in item['instances']:
            if instance == inst['name']:
                conf = inst
    else:
        # Error
        print('Fehler')
    return conf

def umgebung_loeschen(conf, lde_db, envid):
    db = sqlite.create(conf['dba']['lde'][lde_db])
    db = sqlite.query(db, 'remove', [envid])

def umgebungen_laden(conf, lde_db, host, instance):
    dev_db = sqlite.create(conf['dba']['lde'][lde_db])
    db_conf = prepare_config(conf, host, instance)
    db = None
    if db_conf['driver'] == 'MSSQL':
        cond = ''
        if instance is None:
            cond = 'none'
        else:
            cond = host + '\\' + instance
        db = sqlite.query(dev_db, 'umgebungen', [cond])
    if db_conf['driver'] == 'Oracle':
        if instance is None:
            cond = 'none'
        else:
            cond = db_conf['lde_conf']
        db = sqlite.query(dev_db, 'umgebungen', [cond])
    if db_conf['driver'] == 'MySQL':
        db = sqlite.query(dev_db, 'umgebungen', [db_conf['lde_conf']])
    return db


def umgebung_suchen(umgebungen, db_name):
    found = []
    for umgebung in umgebungen:
        if db_name.upper() == umgebung[0].decode("cp1252").upper():
            found.append([umgebung[1].decode("cp1252"), umgebung[2]])
    if len(found) > 0:
        return found
    return [['', -1],]
