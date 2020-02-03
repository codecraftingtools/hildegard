# Copyright (c) 2020 Jeffrey A. Webb

import hildegard
import pidgen

import sys

def create_test_component():
    c = pidgen.Hierarchic_Component()
    c.subcomponents["C1"] = pidgen.Component()
    return c

def main(args=None):
    global ui # must be global for program to not hang on exit

    if args is None:
        args = sys.argv
        
    c1 = create_test_component()
    c2 = create_test_component()
    c2.title = "Component 2"
    
    ui = hildegard.Application()
    ui.edit(c1)
    ui.edit(c2)
    return ui.execute()

if __name__ == "__main__":
    sys.exit(main())
