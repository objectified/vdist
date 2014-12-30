#!/usr/bin/env python
import argparse

from vdist.builder import Builder
from vdist.config import ApplicationConfig


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', '--config',
                            help='path to config file', required=True)
    args = arg_parser.parse_args()

    config = ApplicationConfig()
    config.load(args.config)
    config.validate()

    builder = Builder(config)
    builder.run()
