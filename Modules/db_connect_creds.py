#!/usr/bin/env python2.7
"""Functions related to MySQL credentials."""
import logging

DBCONF = './Modules/dbconnect.conf'
# DBCONF = './dbconnect.conf'

def entercreds():
    """Ask user to input credentials."""
    logging.info('Please, enter MySQL credentials.')
    username = raw_input('Enter the DB username: ')
    password = raw_input('Enter the password: ')
    return str(username), str(password)


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
            fhandle.write('%s\n' % username)
            fhandle.write('%s\n' % password)
    except Exception as exception:
        logging.error("Failed to write '%s'.", DBCONF)
        raise exception
