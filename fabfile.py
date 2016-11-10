# -*- coding: utf-8 -*-
"""
    fabfile.py Example
    author: Danilo F. Chilene <bicofino at gmail dot com>
"""
from fabric.api import run, sudo, put, prompt, cd, env, get, task, lrun
from fabric.contrib.files import append
import os

env.roledefs = {
    # My web servers
    'webservers': ['web01', 'web02', 'web03', 'web04'],
    # My database servers
    'dbs': ['db01', 'db02', 'db03', 'db04'],
}


@task
def mem_usage():
    '''Check free memory'''
    run('free -m')


@task
def sudo_test():
    '''Testing with sudo'''
    sudo('touch /root/myfile.txt')
    sudo('ls -la /root/myfile.txt')


@task
def put_file():
    '''Copy a local file to a server'''
    put('/tmp/myfile.txt', '/tmp/myfile.txt')
    run('ls /tmp/myfile.txt')


@task
def get_file():
    '''Copy a local file to a server'''
    get('/tmp/myfile.txt', '/tmp/myfile.txt')
    run('ls /tmp/myfile.txt')


@task
def read_key_file(key_file):
    '''Check if a key is public'''
    key_file = os.path.expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()


@task
def push_key(key_file='~/.ssh/id_rsa.pub'):
    '''Push a SSH key'''
    run("rm -rf /home/bicofino/.ssh")
    run("mkdir /home/bicofino/.ssh")
    key_text = read_key_file(key_file)
    run('touch ~/.ssh/authorized_keys')
    append('~/.ssh/authorized_keys', key_text)


@task
def start(service):
    '''Start a service, usage start:service'''
    run("/etc/init.d/{0} start".format(service), warn_only=True)


@task
def status(service):
    '''Get the status from a service, usage status:service'''
    run("/etc/init.d/{0} status".format(service), warn_only=True)


@task
def stop(service):
    '''Stop a service, usage stop:service'''
    run("/etc/init.d/{0} stop".format(service), warn_only=True)


@task
def restart(service):
    '''Restart a service, usage restart:service'''
    stop(service)
    start(service)


@task
def prompt_test():
    '''Just a user prompt test'''
    local = prompt('Type dir to list:')
    dir = '/{0}'.format(local)
    with cd(dir):
        run('ls')


@task
def install(package):
    '''Install a package / apt-get'''
    sudo("apt-get -y install %s" % package)


@task
def asm_disks():
    '''Task to get disk information and ASM disks'''
    disks = []
    sudo('vgdisplay -v')
    sudo('pvdisplay -v')
    sudo('dmesg|grep sd')
    sudo('df -h')
    sudo('cat /etc/fstab')
    disks.append(sudo('/etc/init.d/oracleasm listdisks').splitlines())
    for disk in disks:
        numbers = range(0, len(disk))
        for number in numbers:
            devices = []
            devices.append(
                sudo('/etc/init.d/oracleasm querydisk -d {0}'.format(disk[number])))
            for device in devices:
                partition = device.split('[', 1)[1].split(']')[0]
                sudo(
                    'ls -l /dev |grep {0}|grep {1}'.format(
                        partition.split(',')[0],
                        partition.split(',')[1]))


@task
def remove_pkg_weblogic(
        domain,
        pkg,
        duser,
        dpassword,
        dhostname,
        cluster,
        classpath,
        dport):
    '''Remove a weblogic package(ear)'''
    name = sudo(
        '''cat {0}/config/config.xml |  grep {1}|grep -v argument|sed 's/\(.*<name>\)//' | sed 's/\(<\/name>*\)//'| head -1'''.format(domain, pkg))
    sudo(
        '''/u01/jdk/bin/java -classpath {5} weblogic.Deployer -adminurl t3://{0}:{6} -user {1} -password {2} -undeploy -name {3} -targets {4}'''.format(
            dhostname,
            duser,
            dpassword,
            name,
            cluster,
            classpath,
            dport))


@task
def deploy_weblogic(
        domain,
        pkg,
        classpath,
        duser,
        dpassword,
        upload,
        cluster,
        dhostname,
        dport,
        vm_admin):
    '''Deploy a package(ear) to weblogic'''
    name = sudo(
        '''ls {0}/servers/{2}/upload/{1}*'''.format(domain, pkg, vm_admin))
    name = os.path.basename(name)
    sudo(
        '''/u01/jdk/bin/java -classpath {0} weblogic.Deployer -adminurl t3://{1}:{7} -user {2} -password {3} -stage -distribute -name {4} "{5}{4}" -targets {6}'''.format(
            classpath,
            dhostname,
            duser,
            dpassword,
            name,
            upload,
            cluster,
            dport))
    sudo(
        '''/u01/jdk/bin/java -classpath {0} weblogic.Deployer -adminurl t3://{1}:{6} -user {2} -password {3} -start -name {4} -targets {5}'''.format(
            classpath,
            dhostname,
            duser,
            dpassword,
            name,
            cluster,
            dport))


@task
def stop_weblogic(
        domain,
        pkg,
        duser,
        dpassword,
        dhostname,
        cluster,
        classpath,
        dport):
    '''Stop weblogic VM'''
    sudo(
        '''/u01/jdk/bin/java -classpath {4} weblogic.Admin -url t3://{0}:{5} -username {1} -password {2} STOPCLUSTER -clusterName {3}'''.format(
            dhostname,
            duser,
            dpassword,
            cluster,
            classpath,
            dport))


@task
def start_weblogic(duser, dpassword, dhostname, dport, cluster):
    '''Start weblogic VM'''
    lrun('''/home/oracle/start.sh -u {0} -p {1} -h {2}:{3} -c {4}'''.format(
        duser, dpassword, dhostname, dport, cluster))
