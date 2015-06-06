from __future__ import print_function

import os
import sys

from process_tests import dump_on_error
from process_tests import TestProcess
from process_tests import wait_for_strings

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

TIMEOUT = int(os.getenv('MANHOLE_TEST_TIMEOUT', 10))
HELPER = os.path.join(os.path.dirname(__file__), 'helper.py')


def test_help():
    output = subprocess.check_output(['manhole-cli', '--help'])
    print(output)
    assert output == """usage: manhole-cli [-h] [-t TIMEOUT] [-1 | -2] PID

Connect to a manhole.

positional arguments:
  PID                   A numerical process id, or a path in the form:
                        /tmp/manhole-1234

optional arguments:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout to use. Default: 1 seconds.
  -1, -USR1             Send USR1 (10) to the process before connecting.
  -2, -USR2             Send USR2 (12) to the process before connecting.
"""


def test_usr2():
    with TestProcess(sys.executable, '-u', HELPER, 'test_oneshot_on_usr2') as service:
        with dump_on_error(service.read):
            wait_for_strings(service.read, TIMEOUT, 'Not patching os.fork and os.forkpty. Oneshot activation is done by signal')
            with TestProcess('manhole-cli', '-USR2', str(service.proc.pid), stdin=subprocess.PIPE) as client:
                with dump_on_error(client.read):
                    wait_for_strings(client.read, TIMEOUT, '(ManholeConsole)', '>>>')
                    client.proc.stdin.write("1234+2345\n")
                    wait_for_strings(client.read, TIMEOUT, '3579')


def test_pid():
    with TestProcess(sys.executable, HELPER, 'test_simple') as service:
        with dump_on_error(service.read):
            wait_for_strings(service.read, TIMEOUT, '/tmp/manhole-')
            with TestProcess('manhole-cli', str(service.proc.pid), stdin=subprocess.PIPE) as client:
                with dump_on_error(client.read):
                    wait_for_strings(client.read, TIMEOUT, '(ManholeConsole)', '>>>')
                    client.proc.stdin.write("1234+2345\n")
                    wait_for_strings(client.read, TIMEOUT, '3579')


def test_path():
    with TestProcess(sys.executable, HELPER, 'test_simple') as service:
        with dump_on_error(service.read):
            wait_for_strings(service.read, TIMEOUT, '/tmp/manhole-')
            with TestProcess('manhole-cli', '/tmp/manhole-%s' % service.proc.pid, stdin=subprocess.PIPE) as client:
                with dump_on_error(client.read):
                    wait_for_strings(client.read, TIMEOUT, '(ManholeConsole)', '>>>')
                    client.proc.stdin.write("1234+2345\n")
                    wait_for_strings(client.read, TIMEOUT, '3579')