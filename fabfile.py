# -*- coding: utf-8 -*- 
"""
    fabfile.py Example
    author: Danilo F. Chilene <bicofino at gmail dot com>
"""
from fabric.api import run,sudo,put,prompt,cd,env,get
from fabric.contrib.files import append,exists
import os,sys

env.roledefs = {
    'webservers': ['web01','web02','web03','web04'],                                         # My web servers
}

def mem_usage():
    '''Check free memory'''
    run('free -m')

def sudo_test():
    '''Testing with sudo'''
    sudo('touch /root/myfile.txt')
    sudo('ls -la /root/myfile.txt')

def put_file():
    '''Copy a local file to a server'''
    put('/tmp/myfile.txt', '/tmp/myfile.txt')
    run('ls /tmp/myfile.txt')

def get_file():
    '''Copy a local file to a server'''
    get('/tmp/myfile.txt', '/tmp/myfile.txt')
    run('ls /tmp/myfile.txt')

def read_key_file(key_file):
    key_file = os.path.expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()

def push_key(key_file='~/.ssh/id_rsa.pub'):
    '''Push a SSH key'''
    run("rm -rf /home/bicofino/.ssh")
    run("mkdir /home/bicofino/.ssh")
    key_text = read_key_file(key_file)
    run('touch ~/.ssh/authorized_keys')
    append('~/.ssh/authorized_keys', key_text)

def start(service):
    '''Start a service, usage start:service'''
    run("/etc/init.d/{0} start".format(service),warn_only=True)

def status(service):
    '''Get the status from a service, usage status:service'''
    run("/etc/init.d/{0} status".format(service),warn_only=True)

def stop(service):
    '''Stop a service, usage stop:service'''
    run("/etc/init.d/{0} stop".format(service),warn_only=True)

def restart(service):
    '''Restart a service, usage restart:service'''
    stop(service)
    start(service)

def prompt_test():
    '''Just a user prompt test'''
    local = prompt('Type dir to list:')
    dir = '/{0}'.format(local)
    with cd(dir):
        run('ls')

def install(package):
    '''Install a package / apt-get'''
    sudo("apt-get -y install %s" % package)