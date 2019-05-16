#!/usr/bin/env python

import argparse
import socket
from os import environ
import subprocess
import logging
from sys import argv

from terraformvspherevm.terraformvm import TerraformVM
from terraformvspherevm.terrascriptvspherevm import TerrascriptVSphereVM

from os import pathsep, linesep

logging.basicConfig(format='[%(asctime)s] %(levelname)-5s: %(message)s',level=logging.INFO)

####################
# Main program
####################
def main(main_args = argv):
    logger = logging.getLogger(__name__)
    

    args = argparse.ArgumentParser(
        prog='terraformvspherevm',
        description="Manage vSphere Virtual Machines",
        epilog="When you want to destroy a VM, tfstate file is not required".format(linesep))
    args.add_argument('--action', choices=['create', 'destroy'],
                      required=True,
                      help='Action to Execute against vSphere')
    args.add_argument('--datacenter', action='store',
                      required=True,
                      help='ESXi Datacenter')
    args.add_argument('--datastore', action='store',
                      required=True,
                      help='ESXi Datastore')
    args.add_argument('--pool', action='store',
                      required=True,
                      help='ESXi Resource Pool')
    args.add_argument('--folder', action='store',
                      required=True,
                      help='ESXi VM Folder')
    args.add_argument('--template', action='store',
                      required=True,
                      help='Template Name')
    args.add_argument('--guestid', action='store',
                      required=True,
                      help='Guest ID')
    args.add_argument('--name', action='store',
                      required=True,
                      help='Virtual Machine Name')
    args.add_argument('--nic', action='append',
                      help='Network Interface. Repeat option for several NICs')
    args.add_argument('--ip', action='append',
                      help='NIC IP address. Repeat option for several NICs')
    args.add_argument('--cidr', action='append',
                      help='NIC CIDR. Repeat option for several NICs')
    args.add_argument('--gateway', action='store',
                      help='Default gateway')
    args.add_argument('--cpu', action='store',
                      required=True,
                      help='CPUs')
    args.add_argument('--ram', action='store',
                      required=True,
                      help='Memory')
    args.add_argument('--disk', action='append',
                      help='Additionnal disk in GB. Repeat option for several disks')
    args.add_argument('--dns', action='append',
                      help='DNS server')
    args.add_argument('--esxhost', action='store',
                      required=True,
                      help='ESXi host')
    args.add_argument('--esxuser', action='store',
                      required=True,
                      help='ESXi Username')
    args.add_argument('--esxpassvar', action='store',
                      required=True,
                      help='Environment variable that contain ESXi password')                      
    args.add_argument('--domain', action='store',
                      required=True,
                      help='DNS domain')
    args.add_argument('--dnssearch', action='append',
                      required=True,
                      help='DNS suffix domain')
    args.add_argument('--timezone', action='store',
                      required=True,
                      help='TimeZone')
    args.add_argument('-debug', action='store_true',
                      help='Verbose Output')

    arguments = vars(args.parse_args(main_args[1:]))
    
    if arguments['debug']:
        logger.setLevel(logging.DEBUG)
        logger.debug("DEBUG logging is active")

    logger.debug(environ)
    vmProperties = dict(arguments)
    vmProperties['esxiPassword'] = environ[arguments['esxpassvar']]
    
    logger = logging.getLogger()
    if vmProperties['nic'] is not None:
        if (len(vmProperties['nic']) != len(vmProperties['ip'])):
            logger.critical("The number of --ip must be equal to --nic")
            raise Exception

        if (len(vmProperties['nic']) != len(vmProperties['cidr'])):
            logger.critical("The number of --cidr must be equal to --nic")
            raise Exception

        for addr in vmProperties['ip']:
            try:
                socket.inet_aton(addr)
                # legal
            except socket.error:
                logger.critical("{} is not a valid IP address".format(addr))
                raise Exception

    vm = TerrascriptVSphereVM(
        vmProperties['name'],
        vmProperties['guestid'],
        vmProperties['cpu'],
        vmProperties['ram'],
        vmProperties['folder'])

    vm.setProvider(
        vmProperties['esxhost'],
        vmProperties['esxuser'],
        vmProperties['esxiPassword'])

    vm.setDatacenter(vmProperties['datacenter'])
    vm.setDatastore(vmProperties['datastore'])
    vm.setResourcePool(vmProperties['pool'])
    vm.setTemplate(vmProperties['template'])
    vm.setTimezone(vmProperties['timezone'])
    vm.setDomain(vmProperties['domain'])
    vm.setGateway(vmProperties['gateway'])
    for dns in vmProperties['dns']:
        vm.addDns(dns)

    for search in vmProperties['dnssearch']:
        vm.addSuffix(search)

    if vmProperties['disk'] is not None:
        for idx, size in enumerate(vmProperties['disk']):
            vm.addDisk(size)

    if vmProperties['nic'] is not None:
        for idx, nic in enumerate(vmProperties['nic']):
            vm.addNetworkInterface(
                nic,
                vmProperties['ip'][idx],
                vmProperties['cidr'][idx])
 
    tvm = TerraformVM()
    tvm.addVM(vm)
    if arguments['action'] == 'create':
        tvm.createVM(arguments['name'])
    elif arguments['action'] == 'destroy':
        tvm.destroyVM(arguments['name'])

    exit(0)
