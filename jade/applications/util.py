# TODO: Dedupe with utilities and application framework from ores?
import glob
import os.path
import yamlconf
import logging
import logging.config
import sys

DEFAULT_DIRS = ["config/", "/etc/jade/"]
DEFAULT_LOGGING_CONFIG = "logging_config.yaml"
DEFAULT_FORMAT = "%(asctime)s %(levelname)s:%(name)s -- %(message)s"


logger = logging.getLogger(__name__)


def build_config(config_dirs=DEFAULT_DIRS, **kwargs):
    # Loads files in alphabetical order based on the bare filename
    config_file_paths = []
    for directory in config_dirs:
        dir_glob = os.path.join(directory, "*.yaml")
        config_file_paths.extend((os.path.basename(path), path)
                                 for path in glob.glob(dir_glob))
    config_file_paths.sort()
    logger.info("Loading configs from {0}".format(config_file_paths))
    config = yamlconf.load(*(open(p) for fn, p in config_file_paths))

    return config


def configure_logging(verbose=False, debug=False, logging_config=None,
                      **kwargs):
    # Load logging config if specified.  If no config file is specified, we
    # make a half-hearted attempt to find a distributed logging_config.yaml
    # in the current working directory.
    if logging_config is None:
        if os.path.exists(DEFAULT_LOGGING_CONFIG):
            logging_config = DEFAULT_LOGGING_CONFIG

    if logging_config is not None:
        with open(logging_config) as f:
            logging_config = yamlconf.load(f)
            logging.config.dictConfig(logging_config)

        # Secret sauce: if running from the console, mirror logs there.
        if sys.stdin.isatty():
            handler = logging.StreamHandler(stream=sys.stderr)
            formatter = logging.Formatter(fmt=DEFAULT_FORMAT)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)

    else:
        # Configure fallback logging.
        logging.basicConfig(level=logging.INFO, format=DEFAULT_FORMAT)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
