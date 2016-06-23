============
Introduction
============

This introduction will show how to use **mecoSHARK**. Furthermore, we list all requirements for this tool here, so that an
easy installation is possible.

**This software is highly experimental and still in development.**





The complete documentation can be found here: `documentation <http://ftrautsch.github.io/mecoSHARK/index.html>`_.

The documentation can also be built via

	.. code-block:: bash

		$ sphinx-build -b html docs/source docs/build


For the documentation `sphinx <http://sphinx-doc.org/>`_ is used. Be aware, that if **mecoSHARK** is not working on your computer, the API documentation is empty as sphinx autodoc extension requires a runnable script.


.. _requirements:

Requirements
============
There are several requirements for **mecoSHARK**:

*	Python3+ (only tested with python 3.5.0)
*	Mongoengine (0.10.5) - available here: http://mongoengine.org/
*	Pymongo (3.2) - available here: https://api.mongodb.org/python/current/
*   vcsSHARK (0.1) - available here: https://github.com/ftrautsch/vcsSHARK/
*   Sourcemeter (8.0.0-x64-linux) - available here: http://www.sourcemeter.com/download/
*   Sloccount (2.26) - available here: http://www.dwheeler.com/sloccount/
*   Ant (1.9.7) - available here: http://archive.apache.org/dist/ant/binaries/
*   Maven (3.2.5) - available here: https://archive.apache.org/dist/maven/maven-3/


It may be possible, that **mecoSHARK** also works with other versions of the named libraries. But we only tested the versions, which are given in brackets.


How to Use
==========
The installation of mecoSHARK is described in the offical documentation (see above).

.. _usage:

Usage
-----

**vcsSHARK must be executed BEFORE mecoSHARK, as it uses information gathered by vcsSHARK.**

Example:

    .. code-block:: bash

        $ python3.5 mecoSHARK/main.py -i /home/user/projects/projectA -o /home/user/output -r 0789c9728bff02ed4908242139fe0c257a0ad73b -u https://github.com/a1studmuffin/SpaceshipGenerator -U root -P root -DB test -H localhost -p 27017 -a admin



Small Tutorial
--------------

1) Clone project that you want to analyze:

	.. code-block:: bash

		$ git clone https://github.com/ftrautsch/vcsSHARK ~/projects/vcsSHARK

2) Install vcsSHARK and execute it:

	.. code-block:: bash

		$ vcsshark -D mongo -U root -P root -DB test -H localhost -p 27017 -u ~/checkstyle -a admin

3) Set the project to the revision you want to analyze

	.. code-block:: bash

		$ git reset --hard f1ab8c5c6ca8c8a14c585ae086f589d4bd6edca7

4) Start mecoshark

    .. code-block:: bash

		$ python3.5 mecoSHARK/main.py -i ~/projects/vcsSHARK -o ~/output -r f1ab8c5c6ca8c8a14c585ae086f589d4bd6edca7 -u https://github.com/ftrautsch/vcsSHARK -U root -P root -DB test -H localhost -p 27017 -a admin