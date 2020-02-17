# Copyright (c) 2020 Jeffrey A. Webb

from hildegard.diagram import Block, Diagram
from hildegard import Environment
from pidgen import component

import sys

def main(args=None):
    global env # must be global to keep program from hanging on exit

    if args is None:
        args = sys.argv

    env = Environment()

    h1 = component.Hierarchy(
        name="Component 1",
        subcomponents=(
            ("Sub1", component.Instance()),
            ("Sub2", component.Instance()),
        )
    )

    d1 = Diagram(
        hierarchy=h1,
        symbols=(
            ("SC1", Block(instance=h1.subcomponents["Sub1"])),
            ("SC2", Block(instance=h1.subcomponents["Sub2"])),
        )
    )
    env.open(d1)

    b1 = Block(
        instance=Block(instance=h1.subcomponents["Sub2"]),
    )
    env.open(b1)
    
    d2 = Diagram(
        hierarchy=h1,
        symbols=(
            ("MySC2", Block(instance=h1.subcomponents["Sub2"])),
        )
    )
    env.open(d2)
    
    return env.execute()

if __name__ == "__main__":
    sys.exit(main())
