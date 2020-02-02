# Copyright (c) 2020 Jeffrey A. Webb

import hildegard
import pidgen

import sys

def create_test_component():
    c = pidgen.Hierarchic_Component()
    c.subcomponents["C1"] = pidgen.Component()
    return c

def main(args=None):
    if args is None:
        args = sys.argv
        
    c = create_test_component()
    
    global ui # required to exit when UI finished
    
    ui = hildegard.Application()
    ui.edit(c)
    return ui.execute()

if __name__ == "__main__":
    sys.exit(main())
