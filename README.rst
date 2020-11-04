=========
Hildegard
=========

Hildegard is a hierarchic layout and design environment for generating
applications and rendering diagrams.  This graphical schematic editor
will eventually enable the construction of hierarchic software
components and applications by drawing block diagrams.

`Hildegard <hildegard_>`_ is part of the `Code Craftsmen`_ project.
The `documentation`_ and `source code`_ can be found on `GitHub`_.

Status
======

The current implementation is only a proof-of-concept prototype.  It
can be used to create block diagrams, but can't be used to generate
code.  It currently saves diagrams in a `YAML-based`_ file format,
which will change to a `Wumps-based`_ format in the future.

Installation Notes
==================

Hildegard is written in `Python 3`_ and requires the `libavoid`_ and
`qtpy`_ Python packages to operate.  Please set up a ``codecraftsmen``
virtual Python environment using `virtualenvwrapper`_ and then follow
the installation instructions for each of these prerequisite packages.

The current implementation also requires the `PyYAML`_ Python package,
which can be installed like this::

  workon codecraftsmen
  pip install pyyaml

Make sure that `Git`_ is installed and then pull down the Hildegard
source code from `GitHub`_ using these commands::

  mkdir -p ~/git
  cd ~/git
  git clone https://github.com/codecraftingtools/hildegard.git

No futher installation is required.  The ``hildegard`` application can
be executed like this::

  workon codecraftsmen
  cd ~/git/hildegard
  ./scripts/hildegard

.. _hildegard: https://www.codecraftsmen.org/software.html#hildegard
.. _Code Craftsmen: https://www.codecraftsmen.org
.. _documentation:
      https://github.com/codecraftingtools/hildegard/blob/master/README.rst
.. _source code: https://github.com/codecraftingtools/hildegard
.. _GitHub: https://www.codecraftsmen.org/foundation.html#github
.. _YAML-based: https://yaml.org
.. _Wumps-based: https://www.codecraftsmen.org/software.html#wumps
.. _Python 3: https://www.codecraftsmen.org/foundation.html#python
.. _libavoid: https://www.codecraftsmen.org/libavoid-notes.html#libavoid-install
.. _qtpy: https://www.codecraftsmen.org/qt-notes.html#qt-install
.. _virtualenvwrapper:
      https://www.codecraftsmen.org/virtualenvwrapper-notes.html#virtualenvwrapper-install
.. _PyYAML: https://pyyaml.org
.. _Git: https://www.codecraftsmen.org/git-notes.html#git-install
