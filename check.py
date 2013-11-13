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


def die(why):
    '''Tell what happened then bail out.'''
    
    print("status {0}".format(str(why).strip('\n')))
    exit(1)


def get_config():
    '''Return a config dict or None if no config file.'''
    
    locations = ['/etc/agent.pgep.ini', 'agent.pgep.ini']
    
    for loc in locations:
        if isfile(loc):
            config = ConfigObj(loc)
            break
    else:
        die("Couldn't find a config file")
    
    return config


def select_one(**kwargs):
    '''Return a string describing whether you could select 1.
    
    psycopg2 follows PEP 249 so parameters can be seen in the footnotes at
    http://www.python.org/dev/peps/pep-0249/#id40
    
    Also see basic connection parameters defined at:
    http://initd.org/psycopg/docs/module.html#psycopg2.connect
    
    (These constitute what you can put in the config file.)
    '''
    
    try:
        conn = psycopg2.connect(**kwargs)
        cur = conn.cursor()
        cur.execute("select 1;")
        result = cur.fetchone()
    except Exception as e:
        die(e)
        
    return result[0]


def spawn():
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', 
                        help='Profile name from config to use for connection')
    args = parser.parse_args()
    config = get_config()
    
    result = select_one(**config['local'])
    
    print("status OK")
    print("metric select_one int32 {0}".format(args.profile))