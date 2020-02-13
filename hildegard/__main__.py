# Copyright (c) 2020 Jeffrey A. Webb

from hildegard import Application
from pidgen import component

import sys

def main(args=None):
    global app # must be global for program to not hang on exit

    if args is None:
        args = sys.argv

    app = Application()

    c1 = component.Hierarchic_Implementation(
        name="Component 1",
        subcomponents=(
            ("SC1", component.Instance()),
        )
    )
    app.open(c1)
    
    c2 = component.Hierarchic_Implementation(
        name="Component 2",
        subcomponents=(
            ("SC2", component.Instance()),
        )
    )
    app.open(c2)
    
    return app.execute()

if __name__ == "__main__":
    sys.exit(main())
