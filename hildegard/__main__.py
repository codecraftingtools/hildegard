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

    d1 = Diagram(
        hierarchy = component.Hierarchy(
            name="Component 1",
            subcomponents=(
                ("SC1", component.Instance()),
                ("SC2", component.Instance()),
            )
        )
    )
    env.open(d1)

    b1 = Block(
        instance = component.Instance(name="SC3"),
    )
    env.open(b1)
    
    d2 = Diagram(
        hierarchy = component.Hierarchy(
            name="Component 2",
            subcomponents=(
                ("SC4", component.Instance()),
            )
        )
    )
    env.open(d2)
    
    return env.execute()

if __name__ == "__main__":
    sys.exit(main())
