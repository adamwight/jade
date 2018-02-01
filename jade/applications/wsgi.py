import docopt_subcommands as dsc
from jade.wsgi import server

from .util import build_config, configure_logging


@dsc.command()
def server_command(args):
    """
    usage:
        {program} server (-h | --help)
        {program} server [--host=<name>] [--port=<num>] [--config-dir=<path>]...
                         [--processes=<num>] [--debug] [--verbose]
                         [--logging-config=<path>]

    Runs a WSGI-based web server that hosts JADE.

    Options:
        -h --help                Print this documentation
        --host=<name>            The hostname to listen on [default: 0.0.0.0]
        --port=<num>             The port number to start the server on
                                 [default: 8080]
        --config-dir=<path>      The path to a directory containing configuration
                                 [default: config/]
        --logging-config=<path>  The path to a logging configuration file
        --processes=<num>        The number of parallel processes to handle
                                 [default: 16]
        --debug                  Print debug logging information
        --verbose                Print verbose extraction information
    """
    host = args['--host']
    port = int(args['--port'])
    processes = int(args['--processes'])
    verbose = args['--verbose']
    debug = args['--debug']

    run(host, port, processes,
        verbose=verbose, debug=debug,
        logging_config=args['--logging-config'],
        config_dirs=args['--config-dir'])


def run(host, port, processes, **kwargs):
    application = build(**kwargs)
    application.debug = True
    application.run(host=host, port=port, processes=processes, debug=True)


def build(**kwargs):
    configure_logging(**kwargs)
    config = build_config(**kwargs)
    return server.configure(config)
