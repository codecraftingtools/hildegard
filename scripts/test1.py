#!/usr/bin/env python3

# Copyright (c) 2020 Jeffrey A. Webb

from pathlib import Path
import sys

# Add the project root directory to sys.path and execute the
# hildegard.__main__ module as a script.
hildegard_root = str(Path(sys.path[0]) / Path(".."))
sys.path.insert(1, hildegard_root)

from hildegard.diagram import Block, Connector, Connection, Diagram
from hildegard import Environment
from pidgen import component

import sys

def main(args=None):
    global env # must be global to keep program from hanging on exit

    if args is None:
        args = sys.argv

    env = Environment()
    
    if1 = component.Interface(
        name="Interface 1",
        ports=(
            ("Port 1", component.Port(name="Port 1")),
            ("Port 2", component.Port(name="Port 2")),
        )
    )
    
    im1 = component.Implementation(
        name="Implementation 1",
        interface=if1,
    )
    
    h1 = component.Hierarchy(
        name="Component 1",
        subcomponents=(
            ("SC1", component.Instance(
                interface=if1,
                implementation=im1,
            )),
            ("SC2", component.Instance(
                interface=if1,
                implementation=im1,
            )),
        )
    )

    d1 = Diagram(
        hierarchy=h1,
        symbols=(
            Block(
                instance=h1.subcomponents["SC1"],
                connectors=(
                    Connector(
                        name="Connector 1",
                        port=if1.ports["Port 1"], row=0,
                    ),
                    Connector(
                        name="Connector 2",
                        port=if1.ports["Port 2"], row=1,
                    ),
                    Connector(
                        name="Connector 3",
                        port=if1.ports["Port 2"], row=2,
                    ),
                )
            ),
            Block(
                instance=h1.subcomponents["SC2"],
                connectors=(
                    Connector(
                        name="Connector 1",
                        port=if1.ports["Port 1"], row=0,
                    ),
                    Connector(
                        name="Connector 2",
                        port=if1.ports["Port 2"], row=1,
                    ),
                )
            )
        )
    )
    d1.connections.extend([
        Connection(
            channel=component.Channel(),
            source=d1.symbols[0].connectors[2],
            sink=d1.symbols[1].connectors[1],
        ),
        Connection(
            channel=component.Channel(),
            source=d1.symbols[0].connectors[1],
            sink=d1.symbols[1].connectors[0],
        ),
    ])
    env.open(d1)

    b1 = Block(
        instance=Block(instance=h1.subcomponents["SC2"]),
    )
    env.open(b1)
    
    d2 = Diagram(
        hierarchy=h1,
        symbols=(
            Block(instance=h1.subcomponents["SC2"]),
        )
    )
    env.open(d2)
    
    return env.execute()

if __name__ == "__main__":
    sys.exit(main())
