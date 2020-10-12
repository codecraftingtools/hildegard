=========
Hildegard
=========

Hildegard is a hierarchic layout and design environment for generating
applications and rendering diagrams.  This graphical schematic editor
will eventually enable the construction of hierarchic software
components and applications by drawing block diagrams.

Hildegard is part of the `Code Craftsmen`_ project.  The latest
`documentation`_ and `source code`_ can be found on `GitHub`_.

Status
======

The current implementation is only a proof-of-concept prototype.  It
can be used to create block diagrams, but can't be used to generate
code.  It currently saves diagrams in a `YAML-based`_ file format,
which will change to a `Wumps-based`_ format in the future.

Installation Notes
==================

Hildegard is written in `Python 3`_, and requires the `libavoid`_ and
`qtpy`_ Python packages to operate.  Please set up a virtual Python
environment using `virtualenvwrapper`_ and then follow the
installation instructions for each of these prerequisite packages.

The current implementation also requires the `PyYAML`_ Python package,
which can be installed like this::

  workon codecraftsmen
  pip install pyyaml

The Hildegard source code can be pulled down from `GitHub`_ using this
`Git`_ command::

  git clone https://github.com/codecraftingtools/hildegard.git

No futher installation is required.  The ``hildegard`` application can
be executed like this::

  workon codecraftsmen
  cd hildegard
  ./scripts/hildegard

.. _Code Craftsmen: https://www.codecraftsmen.org
.. _documentation:
      https://github.com/codecraftingtools/hildegard/blob/master/README.rst
.. _source code: https://github.com/codecraftingtools/hildegard
.. _GitHub: https://www.codecraftsmen.org/foundation.html#github
.. _YAML-based: https://yaml.org
.. _Wumps-based: https://www.codecraftsmen.org/software.html#wumps
.. _Python 3: https://www.codecraftsmen.org/foundation.html#python
.. _libavoid: https://www.codecraftsmen.org/foundation.html#libavoid
.. _qtpy: https://www.codecraftsmen.org/foundation.html#qt
.. _virtualenvwrapper:
      https://www.codecraftsmen.org/foundation.html#virtualenvwrapper
.. _PyYAML: https://pyyaml.org
.. _Git: https://www.codecraftsmen.org/foundation.html#git
