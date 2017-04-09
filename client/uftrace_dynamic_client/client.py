
import argparse
import sys

from uftrace_dynamic_client.communicator import Communicator, CommunicatorException
from uftrace_dynamic_client.ui import Ui
from uftrace_dynamic_client.util import Filter


def print_err(*args, **kwargs):
    """
    Prints to stderr
    :param args: print args
    :param kwargs: print kwargs
    """
    print(*args, **kwargs, file=sys.stderr)


def run_ui(args):
    """
    Runs the ui command
    :param args: The command line arguments
    """
    comm = Communicator()
    try:
        comm.connect(args.port)
    except CommunicatorException:
        print_err('Could not connect, is uftrace started on port %d ?' % args.port)
        exit(1)
    try:
        ui = Ui(comm)
        ui.run()
    except CommunicatorException:
        print_err('Connection lost')
        exit(1)
    except KeyboardInterrupt:
        pass


def run_list(args):
    """
    Runs the list command
    :param args: The command line arguments
    """
    comm = Communicator()
    try:
        comm.connect(args.port)
        fil = Filter(args.filter)
        for f in sorted([f for f in comm.function_list]):
            if fil(f, comm.function_list[f]):
                if comm.function_list[f]:
                    s = '(active)'
                else:
                    s = '(nopped)'
                print(f, s)
    except CommunicatorException:
        print_err('Could not connect, is uftrace started on port %d ?' % args.port)
        exit(1)
    except ValueError:
        print('Invalid filter')
        exit(1)


def run_set(args, value):
    """
    Runs the activate/deactivate command
    :param args: The command line arguments
    :param value: The value to set the functions to
    """
    comm = Communicator()
    try:
        comm.connect(args.port)
    except CommunicatorException:
        print_err('Could not connect, is uftrace started on port %d ?' % args.port)
        exit(1)
    try:
        f = {f: value for f in args.functions}
        comm.function_list = f
    except CommunicatorException:
        print_err('Function not in list')
        exit(1)


def main():
    """
    Entry point function
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('command',
                        choices=['ui', 'list', 'activate', 'deactivate'],
                        help='Command to run, default is \'ui\'', nargs='?', default='ui')
    parser.add_argument('-p', '--port', type=int, help='Port to use, default is \'8000\'', default=8000)
    parser.add_argument('-f', '--filter',
                        help='list command only, Applies a filter to the list of function before printing', default='')
    parser.add_argument('functions',
                        help='activate and deactivate only, list of function to activate/deactivate', nargs='*')

    args = parser.parse_args()

    if args.command == 'ui':
        run_ui(args)
    elif args.command == 'list':
        run_list(args)
    elif args.command == 'activate':
        run_set(args, True)
    elif args.command == 'deactivate':
        run_set(args, False)
    else:
        assert False, 'Not supposed to come here'
