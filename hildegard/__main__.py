# Copyright (c) 2020 Jeffrey A. Webb

import hildegard
import pidgen

import sys

def main(args=None):
    global ui # must be global for program to not hang on exit

    if args is None:
        args = sys.argv

    ui = hildegard.Application()

    c1 = pidgen.Hierarchic_Component(
        title="Component 1",
        subcomponents={"C1": pidgen.Component()},
    )
    ui.edit(c1)
    
    c2 = pidgen.Hierarchic_Component(
        title="Component 2",
        subcomponents={"C2": pidgen.Component()},
    )
    ui.edit(c2)
    
    return ui.execute()

if __name__ == "__main__":
    sys.exit(main())
