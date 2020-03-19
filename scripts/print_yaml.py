#!/usr/bin/env python3

# Copyright (c) 2020 Jeffrey A. Webb

import yaml
import sys
import pprint

def main(args):
    content = open(args[1]).read()
    y = yaml.load(content)
    pprint.pprint(y)
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
