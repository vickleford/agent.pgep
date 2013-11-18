"""
Rackspace Cloud Monitoring plugin for PostgreSQL endpoints as an 
agent.plugin type of check.

Copyright 2013 Victor Watkins <vic.watkins@rackspace.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import argparse
import psycopg2
from sys import exit
from configobj import ConfigObj
from os.path import isfile
from datetime import datetime


class PostgresEndpoint(object):
    '''Represent a postgres endpoint that we can connect to and 
    run a health check against.
    
    psycopg2 follows PEP 249 so kwargs can be seen in the footnotes at
    http://www.python.org/dev/peps/pep-0249/#id40

    Also see basic connection parameters (kwargs here) defined at:
    http://initd.org/psycopg/docs/module.html#psycopg2.connect

    (These constitute what you can put in the config file.)
    '''
    
    def __init__(self, **db_params):
        self.connection = None
        self.cursor = None
        self.start_time = None
        self.tt_connect = None
        self.tt_complete = None
        self.db_params = db_params
        
    def __enter__(self):
        self.start_time = datetime.now()
        self.connection = psycopg2.connect(**self.db_params)
        self.tt_connect = datetime.now()
        self.cursor = self.connection.cursor()
        return self
        
    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.connection.close()

    def select_one(self):
        self.cursor.execute('SELECT 1;')
        result = self.cursor.fetchone()
        self.tt_complete = datetime.now()
        
        return result[0]
        
    def get_connection_time(self):
        td = self.tt_connect - self.start_time
        
        return td.microseconds / 100
        
    def get_complete_time(self):
        td = self.tt_complete - self.start_time
        
        return td.microseconds / 100


def die(why):
    '''Describe what happened and bomb out.'''
    
    msg = str(why).replace('\n', '')
    print("status {0}".format(msg))
    exit(1)
    

def get_config():
    '''Return a config dict or bomb if no config file.'''
    
    locations = ['/etc/agent.pgep.ini', 'agent.pgep.ini']
    
    for loc in locations:
        if isfile(loc):
            config = ConfigObj(loc)
            break
    else:
        die("Couldn't find a config file")
    
    return config


def spawn():
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', 
                        help='Profile name from config to use for connection')
    args = parser.parse_args()
    
    config = get_config()
    
    try:
        with PostgresEndpoint(**config[args.profile]) as pgep:
            result = pgep.select_one()
            tt_connect = pgep.get_connection_time()
            tt_complete = pgep.get_complete_time()
    
        print("status OK")
        print("metric select_one int32 {0}".format(result))
        print("metric tt_connect int32 {0}".format(tt_connect))
        print("metric tt_complete int32 {0}".format(tt_complete))
    except Exception as e:
        die(e)