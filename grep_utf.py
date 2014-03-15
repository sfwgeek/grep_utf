#! /usr/bin/env python2.7
# vim: et sw=4 ts=4:
"""
DESCRIPTION:
    A Command Line Interface (CLI) program to grep Unicode encoded files.
    The Byte Order Mark (BOM) at the start of a file is used to decide what encoding the file is stored in.
    Arguments with spaces should be encolsed in double quotes (").
AUTHOR:
    sfw geek
NOTES:
    <PROG_NAME> = ProgramName
    <FILE_NAME> = <PROG_NAME>.py = ProgramName.py

    Static Analysis:
        pychecker.bat <FILE_NAME>
        pylint <FILE_NAME>
    Profile code:
        python -m cProfile -o <PROG_NAME>.prof <FILE_NAME>
    Vim:
        Remove redundant trailing white space: '\s\+$'.
    Python Style Guide:
        http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
    Docstring Conventions:
        http://www.python.org/dev/peps/pep-0257
"""


# FUTURE STATEMENTS (compiler directives).
# Enable Python 3 print() functionality.
from __future__ import print_function


# VERSION.
# http://en.wikipedia.org/wiki/Software_release_life_cycle
__version__ = '2014.03.15.01' # Year.Month.Day.Build (YYYY.MM.DD.BB).
__release_stage__ = 'General Availability (GA)' # Phase.


# MODULES.
# http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Imports_formatting
# Standard library imports.
import argparse
import datetime
import sys


# CONSTANTS.
PROGRAM_NAME = sys.argv[0]

# Linux/Unix programs generally use 2 for command line syntax errors and 1 for all other kind of errors.
SYS_EXIT_CODE_SUCCESSFUL = 0
SYS_EXIT_CODE_GENERAL_ERROR = 1
SYS_EXIT_CODE_CMD_LINE_ERROR = 2


# DEFINITIONS.
def usage():
    """Return string detailing how this program is used."""

    return '''
    A Command Line Interface (CLI) program to grep Unicode encoded files.
    The Byte Order Mark (BOM) at the start of a file is used to decide what encoding the file is stored in.
    Arguments with spaces should be encolsed in double quotes (").'''

def getProgramArgumentParser():
    """Return argparse object containing program arguments."""

    argParser = argparse.ArgumentParser(description=usage())

    # Mandatory parameters (though not set as required=True or can not use -V on own).


    # Optional parameters.
    optionalGrp = argParser.add_argument_group('extra optional arguments', 'These arguments are not mandatory.')
    optionalGrp.add_argument('-D', '--duration', action='store_true', dest='duration',
        help='Print to standard output the programs execution duration.')
    optionalGrp.add_argument('-V', '--version', action='store_true', dest='version',
        help='Print the version number to the standard output.  This version number should be included in all bug reports.')

    return argParser

def printVersionDetailsAndExit():
    """Print to standard output programs version details and terminate program."""

    msg = '''
NAME:
    {0}
VERSION:
    {1}
    {2}'''.format(PROGRAM_NAME, __version__, __release_stage__)
    print(msg)
    sys.exit(SYS_EXIT_CODE_SUCCESSFUL)

def getDaySuffix(day):
    """Return st, nd, rd, or th for supplied day."""

    if 4 <= day <= 20 or 24 <= day <= 30:
        return 'th'
    return ['st', 'nd', 'rd'][day % 10 - 1]

def printProgramStatus(started, stream=sys.stdout):
    """Print program duration information."""

    NEW_LINE = '\n'
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f (%a %d{0} %b %Y)'
    finished = datetime.datetime.now()
    delta = finished - started
    dateTimeStr = started.strftime(DATE_TIME_FORMAT.format(getDaySuffix(started.day)))
    msg = '{1}Started:  {0}{1}'.format(dateTimeStr, NEW_LINE)
    dateTimeStr = finished.strftime(DATE_TIME_FORMAT.format(getDaySuffix(finished.day)))
    msg += 'Finished: {0}{1}'.format(dateTimeStr, NEW_LINE)
    msg += 'Duration: {0} (days hh:mm:ss:ms)'.format(delta)
    print(msg, file=stream)

def main():
    """Program entry point."""

    # Store when program started.
    started = datetime.datetime.now()

    # Get parameters supplied to application.
    argParser = getProgramArgumentParser()
    args = argParser.parse_args()

    # Logic for displaying version details or program help.
    if args.version:
        printVersionDetailsAndExit()

    print('badger')

    if args.duration:
        printProgramStatus(started)


# Program entry point.
if __name__ == '__main__':
    main()