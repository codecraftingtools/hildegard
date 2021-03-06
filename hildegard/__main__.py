# Copyright (c) 2020 Jeffrey A. Webb

from hildegard.diagram import Diagram
from hildegard import Environment

import argparse
import sys

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        metavar="FILE",
        nargs="?",
        default = None,
        help="Input file to open",
    )
    return parser

def main(argv=None):
    global env # must be global to keep program from hanging on exit

    if argv is None:
        argv = sys.argv[1:]
        
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.input_file:
        source = args.input_file
    else:
        source = [Diagram(name="Untitled")]
        
    env = Environment(source)
    for entity in env.entities():
        env.view(entity)
        
    return env.execute()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
