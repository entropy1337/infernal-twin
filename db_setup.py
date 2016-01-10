#!/usr/bin/env python2.7
"""Test MySQL connection."""
import MySQLdb
import db_connect_creds
import logging
import os
import sys
import traceback

INFERNAL_DB = 'InfernalWireless'

def _test_mysql_conn():
    """Test MySQL DB connection and return user and pass on success."""
    while True:
        username, password = db_connect_creds.entercreds()
        try:
            dbconn = MySQLdb.connect('localhost',
                                     user=username,
                                     passwd=password)
            dbconn.close()
            break
        except KeyboardInterrupt:
            logging.info('Keybord interrupt.')
            sys.exit(1)
        except Exception:
            logging.error(("Failed to connect to MySQL DB as user '%s', "
                           "password '%s'."), username, password)
            logging.error(traceback.format_exc())

    return username, password

def main():
    """Main."""
    os.system('/etc/init.d/mysql start')
    username, password = _test_mysql_conn()
    db_connect_creds.write_creds(username, password)

    dbconn = MySQLdb.connect('localhost', user=username, passwd=password)
    dbcurr = dbconn.cursor()
    create_db = 'CREATE DATABASE IF NOT EXISTS %s' % INFERNAL_DB
    logging.debug(create_db)
    dbcurr.execute(create_db)

    grant_all = "GRANT ALL ON %s.* TO '%s'@'localhost'" % (INFERNAL_DB, username)
    if password != '':
        grant_all = "%s IDENTIFIED BY '%s'" % (grant_all, password)

    logging.debug(grant_all)
    dbcurr.execute(grant_all)
    dbconn.close()

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
