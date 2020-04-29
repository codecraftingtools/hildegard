#!/usr/bin/env python3

# Copyright (c) 2020 Jeffrey A. Webb

import sys

f = open(sys.argv[1])
for line in f:
    s = line.strip()
    if s.startswith("source:"):
        id = s.split(":")[-1].strip()
        indent = ' '*line.index("source")
        sys.stdout.write(f"{indent}source:\n")
        sys.stdout.write(f"{indent}  - Endpoint:\n")
        sys.stdout.write(f"{indent}      connector: {id}\n")
    elif s.startswith("sink:"):
        id = s.split(":")[-1].strip()
        indent = ' '*line.index("sink")
        sys.stdout.write(f"{indent}sink:\n")
        sys.stdout.write(f"{indent}  - Endpoint:\n")
        sys.stdout.write(f"{indent}      connector: {id}\n")
    else:
        sys.stdout.write(line)
