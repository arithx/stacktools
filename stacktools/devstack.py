"""
Copyright 2013-2014 Rackspace

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


def entry_point():
    pass
