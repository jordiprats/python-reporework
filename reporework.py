#!/usr/bin/env python

from __future__ import print_function

"""
reporework
"""

import os
import sh
import sys
import json
import time
import argparse
from pathlib import Path
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

    try:
        el_guapo = config.get('github', 'guapo').strip('"').strip("'").strip()
        el_bo = config.get('github', 'bo').strip('"').strip("'").strip()
        el_dolent = config.get('github', 'dolent').strip('"').strip("'").strip()
    except:
        sys.exit('MAJOR ERROR')

    user_jordiprats = g.get_user(el_guapo)
    org_saltait = g.get_organization(el_bo)

    print("> stage 1")

    for repo in user_jordiprats.get_repos():
        if 'eyp-' in repo.name and repo.fork:
            if repo.parent:
                if el_dolent in repo.parent.full_name:
                    name = repo.name.split('-')[1]
                    print('rename '+repo.full_name)
                    repo.edit(name='prefork-'+name)
                    time.sleep(10)

    print("> stage 2")

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

    print("> stage 3")

    for repo in org_saltait.get_repos():
        if 'eyp-' in repo.name and not repo.fork:
            name = repo.name.split('-')[1]
            try:
                u_repo = user_jordiprats.get_repo('eyp-'+name)
                if u_repo.name == 'eyp-'+name:
                    print(repo.full_name+' already found - '+u_repo.clone_url)
                else:
                    print(repo.name+' forked')
                    repo.create_fork()
                    time.sleep(30)
            except:
                repo.create_fork()
                print(repo.name+' forked')
                time.sleep(30)

    print("> stage 4")

    for repo in user_jordiprats.get_repos():
        if 'prefork-' in repo.name and repo.fork:
            name = repo.name.split('-')[1]

            # print(repo.parent.full_name)
            if el_dolent in repo.parent.full_name:
                    
                    new_repo = user_jordiprats.get_repo('eyp-'+name)
                    if new_repo:
                        print('deleted: '+repo.name+' new: '+new_repo.full_name)
                        repo.delete()
                        time.sleep(10)
            else:
                if el_bo in repo.parent.full_name:
                    if 'prefork-' in repo.name:
                        repo.edit(name='eyp-'+name)
                print('to KEEP: '+repo.full_name+' forked from '+repo.parent.full_name)

    print("> stage 5")

    for repo in user_jordiprats.get_repos():
        if 'eyp-' in repo.name and repo.fork:
            if not Path('/home/jprats/git/'+repo.name+'/.git/config').is_file():
                print('cloning: '+repo.name)
                sh.git.clone(repo.clone_url, '/home/jprats/git/'+repo.name, _env={"GIT_SSH_COMMAND": "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"})
                time.sleep(10)
            else:
                print('ALREADY THERE: '+repo.full_name)

    print("> stage 6")

    for repo in user_jordiprats.get_repos():
        if repo.parent:
            if el_dolent in repo.parent.full_name:
                print('TODO: '+repo.full_name)


if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './reporework.config'
    do_stuff(config_file=config_file)
