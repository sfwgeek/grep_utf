#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
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

    # View files as binary.
    od -cx <file> | less
    od -ct x1 <file> | less # better alignment.
"""


# FUTURE STATEMENTS (compiler directives).
# Enable Python 3 print() functionality.
from __future__ import print_function


# VERSION.
# http://en.wikipedia.org/wiki/Software_release_life_cycle
__version__ = '2014.03.23.01' # Year.Month.Day.Build (YYYY.MM.DD.BB).
__release_stage__ = 'Beta' # Phase.


# MODULES.
# http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Imports_formatting
# Standard library imports.
import argparse
import codecs
import datetime
import glob
import os
import re
import string
import sys
#from pprint import pprint # DEBUG.


# CONSTANTS.
PROGRAM_NAME = sys.argv[0]

# Linux/Unix programs generally use 2 for command line syntax errors and 1 for all other kind of errors.
SYS_EXIT_CODE_SUCCESSFUL = 0
SYS_EXIT_CODE_GENERAL_ERROR = 1
SYS_EXIT_CODE_CMD_LINE_ERROR = 2

#IO_STREAM_ENCODING_DEFAULT = 'CP850' # Displays £ correctly in command prompt but not if redirect to a file.
IO_STREAM_ENCODING_DEFAULT = 'latin1'
#IO_STREAM_ENCODING_DEFAULT = 'utf-8'

NEW_LINE = '\n'


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
    argParser.add_argument('pattern', nargs=1,
        help='Pattern used to search file lines for.')
    argParser.add_argument('files', nargs='+',
        help='File name/path or file glob')

    # Optional parameters.
    optionalGrp = argParser.add_argument_group('extra optional arguments', 'These arguments are not mandatory.')
    optionalGrp.add_argument('-e', '--regexp', action='store_true', dest='regexp',
        help='Use regular expression in PATTERN.')
    optionalGrp.add_argument('-i', '--ignore-case', action='store_true', dest='ignorecase',
        help='Ignore case distinctions in input PATTERN.')
    optionalGrp.add_argument('-l', '--files-with-matches', action='store_true', dest='noline',
        help='Suppress normal output; instead print the name of each input file from which output would normally have been printed.'
            + '  The scanning will stop on the first match.')
    optionalGrp.add_argument('-n', '--line-number', action='store_true', dest='linenum',
        help='Prefix each line of output with the 1 based line number within its input file.')
    optionalGrp.add_argument('-r', '--recursive', action='store_true', dest='recursive',
        help='Read all files under each directory, recursively.')

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
    printStdout(msg)
    sys.exit(SYS_EXIT_CODE_SUCCESSFUL)

def getDaySuffix(day):
    """Return st, nd, rd, or th for supplied day."""

    if 4 <= day <= 20 or 24 <= day <= 30:
        return 'th'
    return ['st', 'nd', 'rd'][day % 10 - 1]

def printProgramStatus(started):
    """Print program duration information."""

    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f (%a %d{0} %b %Y)'
    finished = datetime.datetime.now()
    delta = finished - started
    dateTimeStr = started.strftime(DATE_TIME_FORMAT.format(getDaySuffix(started.day)))
    msg = '{1}Started:  {0}{1}'.format(dateTimeStr, NEW_LINE)
    dateTimeStr = finished.strftime(DATE_TIME_FORMAT.format(getDaySuffix(finished.day)))
    msg += 'Finished: {0}{1}'.format(dateTimeStr, NEW_LINE)
    msg += 'Duration: {0} (days hh:mm:ss:ms)'.format(delta)
    printStdout(msg)

def printStd(msg, encoding, stream, end):
    encodedMsg = msg.encode(encoding)
    print(encodedMsg, file=stream, end=end)

def printStderr(msg, encoding=IO_STREAM_ENCODING_DEFAULT, end=NEW_LINE):
    """Prints to standard error IO stream in specific encoding."""
    printStd(msg, encoding, sys.stderr, end=end)

def printStderrAndExit(msg, encoding=IO_STREAM_ENCODING_DEFAULT):
    """Prints to standard error IO stream in specific encoding and exits program with error status."""
    printStderr(msg, encoding)
    sys.exit(SYS_EXIT_CODE_CMD_LINE_ERROR)

def printStdout(msg, encoding=IO_STREAM_ENCODING_DEFAULT, end=NEW_LINE):
    """Prints to standard output IO stream in specific encoding."""
    printStd(msg, encoding, sys.stdout, end=end)

def printError(arg, msg):
    """Print error to standard error IO stream."""
    msg = '{0}: {1}: {2}'.format(PROGRAM_NAME, arg, msg)
    printStderr(msg)

def getFileEncoding(fileBOM):
    """Files can contain Byte Order MARK (BOM) at start of file, first 4 bytes.
    Return None if no matching BOM found."""

    # TODO: perf - maybe change startswith() with slice comparison?
    if (fileBOM.startswith(codecs.BOM_UTF32) or
        fileBOM.startswith(codecs.BOM_UTF32_LE) or
        fileBOM.startswith(codecs.BOM_UTF32_BE)):
        return 'utf-32'
    if (fileBOM.startswith(codecs.BOM_UTF16) or
        fileBOM.startswith(codecs.BOM_UTF16_LE) or
        fileBOM.startswith(codecs.BOM_UTF16_BE)):
        return 'utf-16'
    if fileBOM.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig' # Skips BOM.
        #return 'utf-8' # Keeps BOM.

    # No BOM found!
    return None

def getByteOrderMark(firstFileBlock):
    """Return Byte Order Mark (BOM) from file first block."""
    return firstFileBlock[:4]

def getFileBlock(filePath, blockSize=512):
    """Return file block for file."""
    with open(filePath) as srcFO:
        return srcFO.read(blockSize)

def getTextFileEncoding(filePath):
    """Return encoding of file if its a text file, otherwise None."""

    # Assumes filePath is existing file.
    IS_NOT_TEXT_FILE = None
    DEFAULT_ENCODING = 'latin1'
    #DEFAULT_ENCODING = 'ascii'
    #DEFAULT_ENCODING = 'utf-8'

    # Read a block of input/source file.
    fileBlock = getFileBlock(filePath)
    if not fileBlock:
        # Skip empty files.
        return IS_NOT_TEXT_FILE

    fileBOM = getByteOrderMark(fileBlock)
    fileEncoding = getFileEncoding(fileBOM)
    if fileEncoding:
        # File starts with recognised BOM so assume text file.
        return fileEncoding

    if '\0' in fileBlock:
        # Binary file.
        # Point to note, utf-16 files contain alot of '\0' (nulls).
        return IS_NOT_TEXT_FILE

    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    textChars = ''.join(map(chr, range(32, 127)) + list('\n\r\t\b'))
    nullTrans = string.maketrans('', '')
    transStr = fileBlock.translate(nullTrans, textChars)

    # If more than 30% non-text characters, assume a binary file.
    if (len(transStr) / len(fileBlock)) > 0.3:
        # Binary file.
        return IS_NOT_TEXT_FILE

    # Passed all other tests, assume text file.
    return DEFAULT_ENCODING

def printUnicodeStdout(fmtStr, unicodeFmtVals):
    """Format and print Unicode strings."""

    CARRIAGE_RETURN = u'\r'
    LINE_FEED = u'\n' # Newline
    unicodeMsg = unicode(fmtStr).format(*unicodeFmtVals)

    # Stop extra carriage return (\r) appearing.
    unicodeMsg = unicodeMsg.rstrip(CARRIAGE_RETURN + LINE_FEED)
    unicodeMsg += LINE_FEED
    printStdout(unicodeMsg, end='')

def grepFile(patternRE, filePath, fileEncoding, printFileNameOnly, printLineNumber):
    """grep file.  Assumes text file and uses supplied encoding."""

    fileRelPath = os.path.relpath(filePath)
    with codecs.open(filePath, encoding=fileEncoding) as srcFO:
        if printFileNameOnly:
            for line in srcFO:
                if patternRE.search(line):
                    msg = fileRelPath
                    printStdout(msg)
                    break # Scanning will stop on first match (only printing file name).
        if printLineNumber:
            # Print file name, line number and line.
            lineCount = 0
            for line in srcFO:
                lineCount += 1
                if patternRE.search(line):
                    printUnicodeStdout('{0}:{1}:{2}', (fileRelPath, lineCount, line))
        else:
            # Print file name and line.
            for line in srcFO:
                if patternRE.search(line):
                    printUnicodeStdout('{0}:{1}', (fileRelPath, line))

def walkFiles(patternRE, fileArgs, printFileNameOnly, printLineNumber, isRecursive):
    """Iterate the supplied file arguments.
    patternRE - regular expression object to be used to search files.
    fileArgs - list of file names, file paths, file globs, directory names or paths.
    """

    for fileArg in fileArgs:
        if os.path.isfile(fileArg):
            filePath = os.path.abspath(fileArg)
            fileEncoding = getTextFileEncoding(filePath)
            grepFile(patternRE, filePath, fileEncoding, printFileNameOnly, printLineNumber)
        elif os.path.isdir(fileArg):
            if isRecursive:
                # Only grep directory child files if recursive argument set.
                filePaths = []
                fileNames = os.listdir(fileArg)
                for fileName in fileNames:
                    filePath = os.path.join(fileArg, fileName)
                    filePaths.append(filePath)
                walkFiles(patternRE, filePaths, printFileNameOnly, printLineNumber, isRecursive)
            else:
                printError(fileArg, 'Is a directory')
        else:
            # Is file argument a file glob?
            globFiles = glob.glob(fileArg)
            if globFiles:
                walkFiles(patternRE, globFiles, printFileNameOnly, printLineNumber, isRecursive)
            else:
                # Empty list means not file glob.
                printError(fileArg, 'Invalid file glob/path')

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

    patternStr = args.pattern[0]
    fileArgs = args.files

    try:
        if not args.regexp:
            # Escape pattern if not using regular expressions.
            patternStr = re.escape(patternStr)

        compileFlags = 0 # None by default.
        if args.ignorecase:
            compileFlags |= re.IGNORECASE

        # Compile regex pattern (perf reasons).
        patternRE = re.compile(patternStr, compileFlags)
    except:
        msg = 'Invalid regular expression for pattern: {0}'.format(patternStr)
        printStderrAndExit(msg)

    walkFiles(patternRE, fileArgs, args.noline, args.linenum, args.recursive)

    if args.duration:
        printProgramStatus(started)


# Program entry point.
if __name__ == '__main__':
    main()

    # TODO:
    #   - -V (--version) does not work because requirement for 2 arguments (pattern, files)!
    #   - Add thread pool for performance.
    #   - Add consistent error handling for exceptions.
    #   - Group printStd* functions into class.
