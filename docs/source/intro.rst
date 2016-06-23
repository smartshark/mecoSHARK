============
Introduction
============

This introduction will show how to use **mecoSHARK**. Furthermore, we list all requirements for this tool here, so that an
easy installation is possible.

.. WARNING:: This software is highly experimental and still in development.


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

.. NOTE:: It may be possible, that **mecoSHARK** also works with other versions of the named libraries. But we only tested the versions, which are given in brackets.


How to Use
==========
In this chapter, we explain how you can install **mecoSHARK** or use it directly from the command line.


Installation
------------
The installation process is a little bit complicated, as sourcemeter can not be publicly distributed. Thats why you need
to clone **mecoSHARK** and create the following structure:

Overall structure:

.. image:: images/folder_structure.png

Sloccount structure:

.. image:: images/sloccount.png



.. WARNING:: Make sure, that your $JAVA_HOME is set correctly!

.. WARNING:: If you want to use the java parser, download :download:`this script <./_downloads/installMavenWrapper.sh>`, put it into /external/sourcemeter/Java/ and execute it.

.. WARNING:: Make sure, that /external/sloccount2.25 is in your $PATH.

.. _usage:

Usage
-----

.. WARNING:: vcsSHARK must be executed **BEFORE** mecoSHARK, as it uses information gathered by vcsSHARK.

**mecoSHARK** is easy to use. Nevertheless, you need to checkout/clone the repository you want to analyze first. Which means, that the repository at the given **input** path must have the desired revision.

**mecoSHARK** supports different commandline arguments:

.. option:: --help, -h

	shows the help page for this command

.. option:: --version, -v

	shows the version

.. option:: --input <PATH>, -i <PATH>

	path to the repository, which already has the desired revision.

.. option:: --output <PATH>, -o <PATH>

	path to a directory, which can be used as output.

.. option:: --rev <REV>, -r <REV>

	hash of the revision that the project in the given directory has

.. option:: --url <URL>, -u <URL>

	hash of the revision that the project in the given directory has

.. option:: --db-user <USER>, -U <USER>

	mongodb user name

.. option:: --db-password <PASSWORD>, -P <PASSWORD>

	mongodb password

.. option:: --db-database <DATABASENAME>, -DB <DATABASENAME>

	mongodb database name that should be used

.. option:: --db-hostname <HOSTNAME>, -H <HOSTNAME>

	hostname, where the mongodb runs on

.. option:: --db-port <PORT>, -p <PORT>

	port, where the mongodb runs on

.. option:: --db-authentication <DB_AUTHENTICATION> -a <DB_AUTHENTICATION>

	name of the authentication database


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