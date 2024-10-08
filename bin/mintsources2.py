#!/usr/bin/env python3


import argparse
import subprocess

import argcomplete
import os
import shutil
import sys

# Import Application class from mintSources module
sys.path.append('/usr/lib/linuxmint/mintSources/')
from mintSources import Application

SOURCES_FILE = '/etc/apt/sources.list.d/official-source-repositories.list'


def main():
    parser = argparse.ArgumentParser(description='Control official source repositories')
    subparsers = parser.add_subparsers(dest='command')

    status_parser = subparsers.add_parser('status', help='Get the status of official source repositories')
    enable_parser = subparsers.add_parser('enable', help='Enable official source repositories')
    disable_parser = subparsers.add_parser('disable', help='Disable official source repositories')
    toggle_parser = subparsers.add_parser('toggle', help='Toggle official source repositories')

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif args.command == 'status':
        status()
    elif args.command == 'enable':
        enable()
    elif args.command == 'disable':
        disable()
    elif args.command == 'toggle':
        if source_code_repositories_enabled():
            disable()
        else:
            enable()


def source_code_repositories_enabled():
    return os.path.isfile(SOURCES_FILE)


def status():
    if source_code_repositories_enabled():
        print('enabled')
    else:
        print('disabled')


def enable():
    open(SOURCES_FILE, 'w').close()
    reload()


def disable():
    if source_code_repositories_enabled():
        os.remove(SOURCES_FILE)
        reload()


def reload():
    with open("/etc/os-release") as f:
        config = dict([line.strip().split("=") for line in f])
        os_codename = config['VERSION_CODENAME']
    Application(os_codename).apply_official_sources()
    subprocess.run(['sudo', 'apt-get', 'update'], stdout=subprocess.DEVNULL)
    status()


if __name__ == '__main__':
    main()
