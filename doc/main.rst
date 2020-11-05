Status
======

The current implementation is only a proof-of-concept prototype.  It
can be used to create block diagrams, but can't be used to generate
code.  It currently saves diagrams in a `YAML-based`_ file format,
which will change to a `Wumps-based <cc:wumps>` format in the future.

Screenshot
==========

.. figure:: images/screenshot.*

Installation Instructions
=========================

Hildegard is written in `Python 3 <cc:python>` and requires the
`libavoid <cc:libavoid-install>` and `qtpy <cc:qt-install>` Python
packages to operate.  Please set up a ``codecraftsmen`` virtual Python
environment using `virtualenvwrapper <cc:virtualenvwrapper-install>`
and then follow the installation instructions for each of these
prerequisite packages.

The current implementation also requires the `PyYAML`_ Python package,
which can be installed like this::

  workon codecraftsmen
  pip install pyyaml

Make sure that `Git <cc:git-install>` is installed and then pull down
the Hildegard source code from `GitHub <cc:github>` using these
commands::

  mkdir -p ~/git
  cd ~/git
  git clone https://github.com/codecraftingtools/hildegard.git

No futher installation is required.  The ``hildegard`` application can
be executed like this::

  workon codecraftsmen
  cd ~/git/hildegard
  ./scripts/hildegard

.. _YAML-based: https://yaml.org
.. _PyYAML: https://pyyaml.org
