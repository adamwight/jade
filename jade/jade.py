"""
Console access to JADE

Usage:
    jade [-h | --help]
    jade server

Available commands:
    server      Start the web server.

Options:
    --help      Show this usage message.
"""
import docopt_subcommands as dsc

from .applications import wsgi  # noqa: F401


def main():
    dsc.main(program='jade', version='jade v1')
