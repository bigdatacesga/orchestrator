#!/usr/bin/env python
# encoding: utf-8
"""Orquestration template

The following tasks must be implemented:
    - start
    - stop
    - restart
    - status

An instance endpoint has to be provided using the INSTANCE environment variable.
For example:

    INSTANCE="instances/user/cdh/5.7.0/1"

A fabric roledef  is created for each service defined in the registry.
It can be used with the decorator: @roles('servicename1')

WARN: The hosts are accesed using the IP address of the first network device,
usually eth0.

The properties of a given service can be accessed through:

    SERVICES['servicename'].propertyname

for example:

    SERVICES['namenode'].heap

Details about a given node can be obtained through each Node object returned by service.nodes

The fabfile can be tested running it in NOOP mode (testing mode) exporting a NOOP env variable.
"""
from __future__ import print_function
import os
import sys
import json
from fabric.api import *
from fabric.tasks import execute
from fabric.colors import red, green, yellow
from fabric.contrib.files import exists
import registry

env.hosts = ['10.112.243.128', '10.112.243.129']

# Set the username
env.user   = "root"

if os.environ.get('INSTANCE'):
    INSTANCE = os.environ.get('INSTANCE')
else:
    print(red('An instance endpoint has to be provided using the INSTANCE environment variable'))
    sys.exit(2)

if os.environ.get('REGISTRY'):
    REGISTRY = os.environ.get('REGISTRY')
else:
    REGISTRY = 'http://consul.service.int.cesga.es:8500/v1/kv'

# Retrieve info from the registry
registry.connect(REGISTRY)
cluster = registry.Cluster(INSTANCE)
nodes = cluster.nodes
services = cluster.services

# Expose the relevant information
NODES = {node.name: node for node in nodes}
SERVICES = {service.name: service for service in services}
OP = os.environ.get('OP')

print("INSTANCE is: " + INSTANCE)
print("REGISTRY is: " + REGISTRY)
print("OP is: " + OP)

@task
def print_ls():
    result = run("ls /")
    print(result)

def start():
    print("start")
    execute(print_ls, hosts=["root@10.112.243.128"])

def stop():
    print("stop")

def status():
    print("status")

def restart():
    print("restart")

def main():
    if OP == "start":
        start()
    elif OP == "stop":
        stop()
    elif OP == "status":
        status()
    elif OP == "restart":
        restart()
    else:
        print("Error")

main()
