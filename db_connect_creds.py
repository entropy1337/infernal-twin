#!/usr/bin/env python3
"""Test MySQL connection."""
import logging
import MySQLdb

DBCONF = './dbconnect.conf'

def entercreds():
    """Ask user to input credentials."""
    logging.info('Please, enter MySQL credentials.')
    username = input('Enter the DB username: ')
    password = input('Enter the password: ')
    return str(username), str(password)

def main():
    """Main."""
    try:
        username, password = read_creds()
    except Exception:
        username, password = entercreds()

    while True:
        try:
            dbconn = MySQLdb.connect('localhost', user=username,
                                     passwd=password,
                                     db='InfernalWireless')
            logging.info('Connected to MySQL.')
            dbconn.close()
            break
        except Exception as exception:
            logging.error('Failed to connect to MySQL: %s', exception)
            logging.info('Press CTRL+C to terminate.')
            username, password = entercreds()

    write_creds(username, password)

def read_creds():
    """Read credentials from file."""
    try:
        with open(DBCONF, 'r') as fhandle:
            lines = fhandle.readlines()

        return lines[0].rstrip(), lines[1].rstrip()
    except Exception as exception:
        logging.error("Failed to read '%s'.", DBCONF)
        raise exception

def write_creds(username, password):
    """Write credentials into file."""
    try:
        with open(DBCONF, 'w') as fhandle:
            fhandle.write('\n'.join([username, password]))
    except Exception as exception:
        logging.error("Failed to write '%s'.", DBCONF)
        raise exception

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
