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
import subprocess

LOG = logging.getLogger(__name__)


class DeployArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        desc = "Deploys tempest"
        usage_string = """
            tempest-deploy [-p/--path]
        """

        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "-p", "--path", default="/opt/stack/new/tempest", metavar="<path>",
            help="The path to the tempest directory")


class RunArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        desc = "Runs tempest"
        usage_string = """
            tempest-run [-r/--regex] [-c/--concurrency]
        """

        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "-r", "--regex", metavar="<regex>",
            default='(?!.*\[.*\bslow\b.*\])(^tempest\.(api|scenario|thirdparty))',
            help="The test regex to run with tempest")

        self.add_argument(
            "-c", "--concurrency", default=None, metavar="<concurrency>",
            help="Enables concurrency and specifies worker count", type=int)


def initialize_tempest(path):
    subprocess.call(["testr", "init"], cwd=path)


def build_run_options(regex, concurrency=None):
    command = []
    command.append("testr")
    command.append("run")
    command.append(regex)

    if concurrency is not None:
        command.append("--concurrency")
        command.append(concurrency)

    command.append("--subunit")


def build_trace_options():
    command = []
    command.append("subunit-trace")
    command.append("--no-failure-debug")
    command.append("-f")


def run_piped_commands(cmd_a, cmd_b):
    proc_a = subprocess.Popen(
        cmd_a, stdout=subprocess.PIPE, cwd="/opt/stack/new/tempest")
    proc_b = subprocess.Popen(
        cmd_b, stdin=proc_a.stdout, stdout=subprocess.PIPE,
        cwd="/opt/stack/new/tempest")
    proc_a.stdout.close()
    return proc_b.communicate()[0]


def entry_point():
    cl_args = DeployArgumentParser().parse_args()
    initialize_tempest(cl_args.path)


def run_entry_point():
    cl_args = RunArgumentParser().parse_args()
    run_options = build_run_options(
        regex=cl_args.regex, concurrency=cl_args.concurrency)
    trace_options = build_trace_options()
    run_piped_commands(run_options, trace_options)
