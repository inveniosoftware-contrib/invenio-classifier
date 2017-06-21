# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2008, 2009, 2010, 2011, 2013, 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Classifier text extraction from documents like PDF and text.

This module also provides the utility 'is_pdf' that uses GNU file in order to
determine if a local file is a PDF file.
"""

from __future__ import unicode_literals

import codecs
import os
import re
import subprocess

import six
from flask import current_app

from .errors import IncompatiblePDF2Text

_ONE_WORD = re.compile("[A-Za-z]{2,}", re.U)


def is_pdf(document):
    """Check if a document is a PDF file and return True if is is."""
    if not executable_exists('pdftotext'):
        current_app.logger.warning(
            "GNU file was not found on the system. "
            "Switching to a weak file extension test."
        )
        if document.lower().endswith(".pdf"):
            return True
        return False

    # Tested with file version >= 4.10. First test is secure and works
    # with file version 4.25. Second condition is tested for file
    # version 4.10.
    file_output = os.popen('file ' + re.escape(document)).read()
    try:
        filetype = file_output.split(":")[-1]
    except IndexError:
        current_app.logger.error(
            "Your version of the 'file' utility seems to be unsupported."
        )
        raise IncompatiblePDF2Text('Incompatible pdftotext')

    pdf = filetype.find("PDF") > -1
    # This is how it should be done however this is incompatible with
    # file version 4.10.
    # os.popen('file -bi ' + document).read().find("application/pdf")
    return pdf


def text_lines_from_local_file(document, remote=False):
    """Return the fulltext of the local file.

    @param document: fullpath to the file that should be read
    @param remote: boolean, if True does not count lines

    @return: list of lines if st was read or an empty list
    """
    try:
        if is_pdf(document):
            if not executable_exists("pdftotext"):
                current_app.logger.error(
                    "pdftotext is not available on the system."
                )
            cmd = "pdftotext -q -enc UTF-8 %s -" % re.escape(document)
            out = subprocess.Popen(["pdftotext", "-q", "-enc", "UTF-8",
                                    document, "-"],
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE)
            (stdoutdata, stderrdata) = out.communicate()
            lines = stdoutdata.splitlines()
            if not isinstance(stdoutdata, six.text_type):
                # We are in Python 2. We need to cast to unicode
                lines = [line.decode('utf8', 'replace') for line in lines]
        else:
            filestream = codecs.open(document, "r", encoding="utf8",
                                     errors="replace")
            # FIXME - we assume it is utf-8 encoded / that is not good
            lines = [line for line in filestream]
            filestream.close()
    except IOError as ex1:
        current_app.logger.error("Unable to read from file %s. (%s)"
                                 % (document, ex1.strerror))
        return []

    # Discard lines that do not contain at least one word.
    return [line for line in lines if _ONE_WORD.search(line) is not None]


def executable_exists(executable):
    """Test if an executable is available on the system."""
    for directory in os.getenv("PATH").split(":"):
        if os.path.exists(os.path.join(directory, executable)):
            return True
    return False


def get_plaintext_document_body(fpath, keep_layout=False):
    """Given a file-path to a full-text, return a list of unicode strings.

    Each string is a line of the fulltext.
    In the case of a plain-text document, this simply means reading the
    contents in from the file. In the case of a PDF/PostScript however,
    this means converting the document to plaintext.

    :param fpath: (string) - the path to the fulltext file
    :return: (list) of strings - each string being a line in the document.
    """
    textbody = []
    status = 0
    if os.access(fpath, os.F_OK | os.R_OK):
        # filepath OK - attempt to extract references:
        # get file type:
        cmd_pdftotext = [
            current_app.config.get("CLASSIFIER_PATH_GFILE"), fpath
        ]
        pipe_pdftotext = subprocess.Popen(cmd_pdftotext,
                                          stdout=subprocess.PIPE)
        res_gfile = pipe_pdftotext.stdout.read()

        if (res_gfile.lower().find("text") != -1) and \
                (res_gfile.lower().find("pdf") == -1):
            # plain-text file: don't convert - just read in:
            f = open(fpath, "r")
            try:
                textbody = [line.decode("utf-8") for line in f.readlines()]
            finally:
                f.close()
        elif (res_gfile.lower().find("pdf") != -1) or \
                (res_gfile.lower().find("pdfa") != -1):
            # convert from PDF
            (textbody, status) = convert_PDF_to_plaintext(fpath, keep_layout)
        else:
            # invalid format
            status = 1
    else:
        # filepath not OK
        status = 1
    return (textbody, status)


def convert_PDF_to_plaintext(fpath, keep_layout=False):
    """Convert PDF to txt using pdftotext.

    Take the path to a PDF file and run pdftotext for this file, capturing
    the output.

    :param fpath: (string) path to the PDF file
    :return: (list) of unicode strings (contents of the PDF file translated
    into plaintext; each string is a line in the document.)
    """
    if keep_layout:
        layout_option = "-layout"
    else:
        layout_option = "-raw"
    status = 0
    doclines = []
    # Pattern to check for lines with a leading page-break character.
    # If this pattern is matched, we want to split the page-break into
    # its own line because we rely upon this for trying to strip headers
    # and footers, and for some other pattern matching.
    p_break_in_line = re.compile(r'^\s*\f(.+)$', re.UNICODE)
    # build pdftotext command:
    cmd_pdftotext = [current_app.config.get("CLASSIFIER_PATH_PDFTOTEXT"),
                     layout_option, "-q",
                     "-enc", "UTF-8", fpath, "-"]
    current_app.logger.debug("* %s" % ' '.join(cmd_pdftotext))
    # open pipe to pdftotext:
    pipe_pdftotext = subprocess.Popen(cmd_pdftotext, stdout=subprocess.PIPE)

    # read back results:
    for docline in pipe_pdftotext.stdout:
        unicodeline = docline.decode("utf-8")
        # Check for a page-break in this line:
        m_break_in_line = p_break_in_line.match(unicodeline)
        if m_break_in_line is None:
            # There was no page-break in this line. Just add the line:
            doclines.append(unicodeline)
        else:
            # If there was a page-break character in the same line as some
            # text, split it out into its own line so that we can later
            # try to find headers and footers:
            doclines.append(u"\f")
            doclines.append(m_break_in_line.group(1))

    current_app.logger.debug(
        "* convert_PDF_to_plaintext found: %s lines of text" % len(doclines)
    )

    # finally, check conversion result not bad:
    if pdftotext_conversion_is_bad(doclines):
        status = 2
        doclines = []

    return (doclines, status)


def pdftotext_conversion_is_bad(txtlines):
    """Check if conversion after pdftotext is bad.

    Sometimes pdftotext performs a bad conversion which consists of many
    spaces and garbage characters.

    This method takes a list of strings obtained from a pdftotext conversion
    and examines them to see if they are likely to be the result of a bad
    conversion.

    :param txtlines: (list) of unicode strings obtained from pdftotext
    conversion.
    :return: (integer) - 1 if bad conversion; 0 if good conversion.
    """
    # Numbers of 'words' and 'whitespaces' found in document:
    numWords = numSpaces = 0
    # whitespace character pattern:
    p_space = re.compile(unicode(r'(\s)'), re.UNICODE)
    # non-whitespace 'word' pattern:
    p_noSpace = re.compile(unicode(r'(\S+)'), re.UNICODE)
    for txtline in txtlines:
        numWords = numWords + len(p_noSpace.findall(txtline.strip()))
        numSpaces = numSpaces + len(p_space.findall(txtline.strip()))
    if numSpaces >= (numWords * 3):
        # Too many spaces - probably bad conversion
        return True
    else:
        return False
