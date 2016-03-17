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

def create_db(dbcurr, dbname, username, password):
    """Create MySQL DB `dbname` and grant all to `username` with `password` from
    localhost.
    """
    create_dbase = 'CREATE DATABASE IF NOT EXISTS %s' % dbname
    logging.debug(create_dbase)
    dbcurr.execute(create_dbase)

    grant_all = "GRANT ALL ON %s.* TO '%s'@'localhost'" % (dbname, username)
    if password != '':
        grant_all = "%s IDENTIFIED BY '%s'" % (grant_all, password)

    logging.debug(grant_all)
    dbcurr.execute(grant_all)

def create_projects_table(dbcurr):
    """Create MySQL table for Projects."""
    projects_table = '''CREATE TABLE IF NOT EXISTS Projects (ProjectId MEDIUMINT
    NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId),
    AuditorName TEXT, TargetName TEXT, date TEXT)'''
    dbcurr.execute(projects_table)

def create_reports_table(dbcurr):
    """Create MySQL table for Reports."""
    reports_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT
    NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY
    (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT,
    Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES
    Projects (ProjectId))'''
    dbcurr.execute(reports_table)

def main():
    """Main."""
    os.system('/etc/init.d/mysql start')
    username, password = _test_mysql_conn()
    db_connect_creds.write_creds(username, password)

    dbconn = MySQLdb.connect('localhost', user=username, passwd=password)
    dbcurr = dbconn.cursor()
    create_db(dbcurr, INFERNAL_DB, username, password)
    dbconn.close()

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
