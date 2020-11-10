#!/usr/bin/env python

from __future__ import print_function

"""
reporework
"""

import os
import sys
import json
import time
import argparse
from github import Github
from configparser import SafeConfigParser
from distutils.version import LooseVersion

GH_TOKEN = ""
debug = False
write_to = sys.stdout

def eprint(*args, **kwargs):
    global debug
    if debug:
        print(*args, file=sys.stderr, **kwargs)

def do_stuff(config_file, output=sys.stdout):
    global debug, GH_TOKEN, write_to

    write_to=output

    config = SafeConfigParser()
    config.read(config_file)

    try:
        GH_TOKEN = config.get('github', 'token').strip('"').strip("'").strip()    
    except:
        GH_TOKEN = ""
    g = Github(GH_TOKEN)

    try:
        debug = config.getboolean('github', 'debug')
    except:
        debug = False

    user_jordiprats = g.get_user('jordiprats')
    org_saltait = g.get_organization('SaltaIT')

    for repo in user_jordiprats.get_repos():
            if 'eyp-' in repo.name and repo.fork:
                name = repo.name.split('-')[1]
                repo.edit(name='prefork-'+name)

    for repo in user_jordiprats.get_repos():
            if 'prefork-' in repo.name and repo.fork:
                name = repo.name.split('-')[1]
                try:     
                    if org_saltait.get_repo('eyp-'+name):
                        print(name+' already found')
                except:
                    print(name+': syncing')
                    new_repo = org_saltait.create_repo('eyp-'+name,'')
                    new_repo.create_source_import('git', repo.clone_url)
                print('sleeping 300')
                time.sleep(300)



if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './reporework.config'
    do_stuff(config_file=config_file)
