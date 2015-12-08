"""
Copyright 2015-2016 Rackspace

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
import logging
import os
from shutil import copy
import subprocess
import textwrap

from git import Repo

LOG = logging.getLogger(__name__)


class OptionAction(argparse.Action):
    """
        Custom action to ensure that localrc options are not being used when a
        custom localrc file is present.
    """

    def __call__(self, parser, namespace, value, option_string=None):
        if getattr(namespace, 'localrc') is not None:
            parser.error(
                "You cannot set options when using a custom localrc")
        else:
            setattr(namespace, self.dest, value)


class LibvirtTypeAction(argparse.Action):
    """
        Custom action to allow the setting of a libvirt type if the
        -v/--virt-driver option is present and set to libvirt.
    """

    def __call__(self, parser, namespace, value, option_string=None):
        print(namespace.__dict__)
        if getattr(namespace, 'virt_driver') != "libvirt":
            parser.error(
                "LibvirtType can only be specified when virt-driver is libvirt")
        else:
            setattr(namespace, self.dest, value)


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        desc = "Deploys devstack"
        usage_string = """
            devstack-deploy [-l/--localrc] [-v/--virt-driver] [-b/--backend]
                [-t/--libvirt-type]
        """

        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "-l", "--localrc", default=None, metavar="<localrc file>",
            help="Path to a localrc file to be used by the devstack install")

        self.add_argument(
            "-v", "--virt-driver", default=None, metavar="<virt-driver>",
            help="Sets the virt-driver of nova for the default localrc",
            action=OptionAction)

        self.add_argument(
            "-b", "--backend", default=None, metavar="<backend>",
            help="Sets the backend of nova for the default localrc",
            action=OptionAction)

        self.add_argument(
            "-t", "--libvirt-type", default=None, metavar="<libvirt_type>",
            help="Sets the libvirt-type of nova for the default localrc",
            action=LibvirtTypeAction)


def clone_devstack():
    Repo.clone_from(
        'https://github.com/openstack-dev/devstack', '/tmp/devstack/')


def create_stack_user():
    subprocess.call(['/tmp/devstack/tools/create-stack-user.sh'])


def build_localrc(localrc=None, virt_driver=None,
                  backend=None, libvirt_type=None):
    if localrc is not None:
        copy(localrc, '/tmp/devstack/')
        return

    default_localrc = """
        DEST=/opt/stack/new
        DATA_DIR=/opt/stack/data
        MYSQL_PASSWORD=password
        DATABASE_PASSWORD=password
        RABBIT_PASSWORD=password
        ADMIN_PASSWORD=password
        SERVICE_PASSWORD=password
        SERVICE_TOKEN=111222333444
        SWIFT_HASH=1234123412341234
        ROOTSLEEP=0
        ENABLED_SERVICES=c-api,c-bak,c-sch,c-vol,ceilometer-acentral,ceilometer-acompute,ceilometer-alarm-evaluator,ceilometer-alarm-notifier,ceilometer-anotification,ceilometer-api,ceilometer-collector,cinder,dstat,g-api,g-reg,horizon,key,mysql,n-api,n-cond,n-cpu,n-crt,n-net,n-obj,n-sch,rabbit,s-account,s-container,s-object,s-proxy,tempest
        # Screen console logs will capture service logs.
        SCREEN_LOGDIR=/opt/stack/new/screen-logs
        LOGFILE=/opt/stack/new/devstacklog.txt
        VERBOSE=True
        FIXED_RANGE=10.1.0.0/20
        FLOATING_RANGE=172.24.5.0/24
        PUBLIC_NETWORK_GATEWAY=172.24.5.1
        FIXED_NETWORK_SIZE=4096
        SWIFT_REPLICAS=1
        LOG_COLOR=False​
    """

    if virt_driver is not None:
        default_localrc = "{0}\nVIRT_DRIVER={1}".format(
            default_localrc, virt_driver)

    if backend is not None:
        default_localrc = "{0}\nNOVA_BACKEND={1}".format(
            default_localrc, backend)

    if libvirt_type is not None:
        default_localrc = "{0}\nLIBVIRT_TYPE={1}".format(
            default_localrc, libvirt_type)

    with open('/tmp/devstack/localrc', 'w') as outfile:
        outfile.write(textwrap.dedent(default_localrc))


def create_stack():
    subprocess.call(['chown', 'stack:stack', '/tmp/devstack', '-R'])
    subprocess.call(['chmod', '+755', '/tmp/devstack/stack.sh'])
    subprocess.call(['sudo', '-H', '-u', 'stack', '/tmp/devstack/stack.sh'])


def entry_point():
    cl_args = ArgumentParser().parse_args()
    clone_devstack()
    create_stack_user()
    build_localrc(
        localrc=cl_args.localrc, virt_driver=cl_args.virt_driver,
        backend=cl_args.backend, libvirt_type=cl_args.libvirt_type)
    create_stack()
