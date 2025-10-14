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

"""Classifier text normalizer.

This module provides methods to clean the text lines. Currently, the methods
are tuned to work with the output of `pdftotext` and documents in the HEP
field.

This modules uses the refextract module of BibEdit in order to find the
references section and to replace Unicode characters.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from six import iteritems
from .find import find_end_of_reference_section, find_reference_section

import logging

logger = logging.getLogger(__name__)
_washing_regex = []


def get_washing_regex():
    """Return a washing regex list."""
    global _washing_regex
    if len(_washing_regex):
        return _washing_regex

    washing_regex = [
        # Replace non and anti with non- and anti-. This allows a better
        # detection of keywords such as nonabelian.
        (re.compile(r"(\snon)[- ](\w+)"), r"\1\2"),
        (re.compile(r"(\santi)[- ](\w+)"), r"\1\2"),
        # Remove all leading numbers (e.g. 2-pion -> pion).
        (re.compile(r"\s\d-"), " "),
        # Remove multiple spaces.
        (re.compile(r" +"), " "),
    ]

    # Remove spaces in particle names.
    # Particles with -/+/*
    washing_regex += [
        (re.compile(r"(\W%s) ([-+*])" % name), r"\1\2")
        for name in (
            "c",
            "muon",
            "s",
            "B",
            "D",
            "K",
            "Lambda",
            "Mu",
            "Omega",
            "Pi",
            "Sigma",
            "Tau",
            "W",
            "Xi",
        )
    ]

    # Particles followed by numbers
    washing_regex += [
        (re.compile(r"(\W%s) ([0-9]\W)" % name), r"\1\2")
        for name in (
            "a",
            "b",
            "c",
            "f",
            "h",
            "s",
            "B",
            "D",
            "H",
            "K",
            "L",
            "Phi",
            "Pi",
            "Psi",
            "Rho",
            "Stor",
            "UA",
            "Xi",
            "Z",
        )
    ]
    washing_regex += [
        (re.compile(r"(\W%s) ?\( ?([0-9]+) ?\)[A-Z]?" % name), r"\1(\2)")
        for name in ("CP", "E", "G", "O", "S", "SL", "SO", "Spin", "SU", "U", "W", "Z")
    ]

    # Particles with '
    washing_regex += [
        (re.compile(r"(\W%s) ('\W)" % name), r"\1\2") for name in ("Eta", "W", "Z")
    ]

    # Particles with (N)
    washing_regex += [
        (re.compile(r"(\W%s) ?\( ?N ?\)[A-Z]?" % name), r"\1(N)")
        for name in ("CP", "GL", "O", "SL", "SO", "Sp", "Spin", "SU", "U", "W", "Z")
    ]

    # All names followed by ([0-9]{3,4})
    washing_regex.append((re.compile(r"([A-Za-z]) (\([0-9]{3,4}\)\+?)\s"), r"\1\2 "))

    # Some weird names followed by ([0-9]{3,4})
    washing_regex += [
        (re.compile(r"\(%s\) (\([0-9]{3,4}\))" % name), r"\1\2 ")
        for name in ("a0", "Ds1", "Ds2", r"K\*")
    ]

    washing_regex += [
        # Remove all lonel operators (usually these are errors
        # introduced by pdftotext.)
        (re.compile(r" [+*] "), r" "),
        # Remove multiple spaces.
        (re.compile(r" +"), " "),
        # Remove multiple line breaks.
        (re.compile(r"\n+"), r"\n"),
    ]
    _washing_regex = washing_regex
    return _washing_regex


def normalize_fulltext(fulltext):
    """Return a 'cleaned' version of the output provided by pdftotext."""
    # We recognize keywords by the spaces. We need these to match the
    # first and last words of the document.
    fulltext = " " + fulltext + " "

    # Replace some weird unicode characters.
    fulltext = replace_undesirable_characters(fulltext)
    # Replace the greek characters by their name.
    fulltext = _replace_greek_characters(fulltext)

    washing_regex = get_washing_regex()

    # Apply the regular expressions to the fulltext.
    for regex, replacement in washing_regex:
        try:
            fulltext = regex.sub(replacement, fulltext)
        except re.error:
            logger.warning("Found nothing to replace.")

    return fulltext


def cut_references(text_lines):
    """Return the text lines with the references cut."""
    ref_sect_start = find_reference_section(text_lines)
    if ref_sect_start is not None:
        start = ref_sect_start["start_line"]
        end = find_end_of_reference_section(
            text_lines,
            start,
            ref_sect_start["marker"],
            ref_sect_start["marker_pattern"],
        )
        del text_lines[start : end + 1]
    else:
        logger.warning("Found no references to remove.")
        return text_lines

    return text_lines


_GREEK_REPLACEMENTS = {
    "\u00af": " ",
    "\u00b5": " Mu ",
    "\u00d7": " x ",
    "\u0391": " Alpha ",
    "\u0392": " Beta ",
    "\u0393": " Gamma ",
    "\u0394": " Delta ",
    "\u0395": " Epsilon ",
    "\u0396": " Zeta ",
    "\u0397": " Eta ",
    "\u0398": " Theta ",
    "\u0399": " Iota ",
    "\u039a": " Kappa ",
    "\u039b": " Lambda ",
    "\u039c": " Mu ",
    "\u039d": " Nu ",
    "\u039e": " Xi ",
    "\u039f": " Omicron ",
    "\u03a0": " Pi ",
    "\u03a1": " Rho ",
    "\u03a3": " Sigma ",
    "\u03a4": " Tau ",
    "\u03a5": " Upsilon ",
    "\u03a6": " Phi ",
    "\u03a7": " Chi ",
    "\u03a8": " Psi ",
    "\u03a9": " Omega ",
    "\u03b1": " Alpha ",
    "\u03b2": " Beta ",
    "\u03b3": " Gamma ",
    "\u03b4": " Delta ",
    "\u03b5": " Epsilon ",
    "\u03b6": " Zeta ",
    "\u03b7": " Eta ",
    "\u03b8": " Theta ",
    "\u03b9": " Iota ",
    "\u03ba": " Kappa ",
    "\u03bb": " Lambda ",
    "\u03bc": " Mu ",
    "\u03bd": " Nu ",
    "\u03be": " Xi ",
    "\u03bf": " Omicron ",
    "\u03c0": " Pi ",
    "\u03c1": " Rho ",
    "\uc3c2": " Sigma ",
    "\u03c3": " Sigma ",
    "\u03c4": " Tau ",
    "\u03c5": " Upsilon ",
    "\u03c6": " Phi ",
    "\u03c7": " Chi ",
    "\u03c8": " Psi ",
    "\u03c9": " Omega ",
    "\u03ca": " Iota ",
    "\u03cb": " Upsilon ",
    "\u03cc": " Omicron ",
    "\u03cd": " Upsilon ",
    "\u03ce": " Omega ",
    "\u03cf": " Kai ",
    "\u03d0": " Beta ",
    "\u03d1": " Theta ",
    "\u03d2": " Upsilon ",
    "\u03d3": " Upsilon ",
    "\u03d4": " Upsilon ",
    "\u03d5": " Phi ",
    "\u03d6": " Pi ",
    "\u03d7": " Kai ",
    "\u03d8": " Koppa ",
    "\u03d9": " Koppa ",
    "\u03da": " Stigma ",
    "\u03db": " Stigma ",
    "\u03dc": " Digamma ",
    "\u03dd": " Digamma ",
    "\u03de": " Koppa ",
    "\u03df": " Koppa ",
    "\u03e0": " Sampi ",
    "\u03e1": " Sampi ",
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2015": "-",
    "\u2019": "'",
    "\u2032": "'",
    "\u2126": " Omega ",
    "\u2206": " Delta ",
    "\u2212": "-",
    "\u2215": "/",
    "\u2216": "\\",
    "\u2217": "*",
    "\u221d": " Alpha ",
}

# a dictionary of undesirable characters and their replacements:
UNDESIRABLE_CHAR_REPLACEMENTS = {
    # Control characters not allowed in XML:
    "\u2028": "",
    "\u2029": "",
    "\u202a": "",
    "\u202b": "",
    "\u202c": "",
    "\u202d": "",
    "\u202e": "",
    "\u206a": "",
    "\u206b": "",
    "\u206c": "",
    "\u206d": "",
    "\u206e": "",
    "\u206f": "",
    "\ufff9": "",
    "\ufffa": "",
    "\ufffb": "",
    "\ufffc": "",
    "\ufeff": "",
    # Remove the result of a bad UTF-8 character
    "\uffff": "",
    # Language Tag Code Points:
    "\U000e0000": "",
    "\U000e0001": "",
    "\U000e0002": "",
    "\U000e0003": "",
    "\U000e0004": "",
    "\U000e0005": "",
    "\U000e0006": "",
    "\U000e0007": "",
    "\U000e0008": "",
    "\U000e0009": "",
    "\U000e000a": "",
    "\U000e000b": "",
    "\U000e000c": "",
    "\U000e000d": "",
    "\U000e000e": "",
    "\U000e000f": "",
    "\U000e0010": "",
    "\U000e0011": "",
    "\U000e0012": "",
    "\U000e0013": "",
    "\U000e0014": "",
    "\U000e0015": "",
    "\U000e0016": "",
    "\U000e0017": "",
    "\U000e0018": "",
    "\U000e0019": "",
    "\U000e001a": "",
    "\U000e001b": "",
    "\U000e001c": "",
    "\U000e001d": "",
    "\U000e001e": "",
    "\U000e001f": "",
    "\U000e0020": "",
    "\U000e0021": "",
    "\U000e0022": "",
    "\U000e0023": "",
    "\U000e0024": "",
    "\U000e0025": "",
    "\U000e0026": "",
    "\U000e0027": "",
    "\U000e0028": "",
    "\U000e0029": "",
    "\U000e002a": "",
    "\U000e002b": "",
    "\U000e002c": "",
    "\U000e002d": "",
    "\U000e002e": "",
    "\U000e002f": "",
    "\U000e0030": "",
    "\U000e0031": "",
    "\U000e0032": "",
    "\U000e0033": "",
    "\U000e0034": "",
    "\U000e0035": "",
    "\U000e0036": "",
    "\U000e0037": "",
    "\U000e0038": "",
    "\U000e0039": "",
    "\U000e003a": "",
    "\U000e003b": "",
    "\U000e003c": "",
    "\U000e003d": "",
    "\U000e003e": "",
    "\U000e003f": "",
    "\U000e0040": "",
    "\U000e0041": "",
    "\U000e0042": "",
    "\U000e0043": "",
    "\U000e0044": "",
    "\U000e0045": "",
    "\U000e0046": "",
    "\U000e0047": "",
    "\U000e0048": "",
    "\U000e0049": "",
    "\U000e004a": "",
    "\U000e004b": "",
    "\U000e004c": "",
    "\U000e004d": "",
    "\U000e004e": "",
    "\U000e004f": "",
    "\U000e0050": "",
    "\U000e0051": "",
    "\U000e0052": "",
    "\U000e0053": "",
    "\U000e0054": "",
    "\U000e0055": "",
    "\U000e0056": "",
    "\U000e0057": "",
    "\U000e0058": "",
    "\U000e0059": "",
    "\U000e005a": "",
    "\U000e005b": "",
    "\U000e005c": "",
    "\U000e005d": "",
    "\U000e005e": "",
    "\U000e005f": "",
    "\U000e0060": "",
    "\U000e0061": "",
    "\U000e0062": "",
    "\U000e0063": "",
    "\U000e0064": "",
    "\U000e0065": "",
    "\U000e0066": "",
    "\U000e0067": "",
    "\U000e0068": "",
    "\U000e0069": "",
    "\U000e006a": "",
    "\U000e006b": "",
    "\U000e006c": "",
    "\U000e006d": "",
    "\U000e006e": "",
    "\U000e006f": "",
    "\U000e0070": "",
    "\U000e0071": "",
    "\U000e0072": "",
    "\U000e0073": "",
    "\U000e0074": "",
    "\U000e0075": "",
    "\U000e0076": "",
    "\U000e0077": "",
    "\U000e0078": "",
    "\U000e0079": "",
    "\U000e007a": "",
    "\U000e007b": "",
    "\U000e007c": "",
    "\U000e007d": "",
    "\U000e007e": "",
    "\U000e007f": "",
    # Musical Notation Scoping
    "\U0001d173": "",
    "\U0001d174": "",
    "\U0001d175": "",
    "\U0001d176": "",
    "\U0001d177": "",
    "\U0001d178": "",
    "\U0001d179": "",
    "\U0001d17a": "",
    "\u0000": "",  # NULL
    "\u0001": "",  # START OF HEADING
    # START OF TEXT & END OF TEXT:
    "\u0002": "",
    "\u0003": "",
    "\u0004": "",  # END OF TRANSMISSION
    # ENQ and ACK
    "\u0005": "",
    "\u0006": "",
    "\u0007": "",  # BELL
    "\u0008": "",  # BACKSPACE
    # SHIFT-IN & SHIFT-OUT
    "\u000e": "",
    "\u000f": "",
    # Other controls:
    "\u0010": "",  # DATA LINK ESCAPE
    "\u0011": "",  # DEVICE CONTROL ONE
    "\u0012": "",  # DEVICE CONTROL TWO
    "\u0013": "",  # DEVICE CONTROL THREE
    "\u0014": "",  # DEVICE CONTROL FOUR
    "\u0015": "",  # NEGATIVE ACK
    "\u0016": "",  # SYNCRONOUS IDLE
    "\u0017": "",  # END OF TRANSMISSION BLOCK
    "\u0018": "",  # CANCEL
    "\u0019": "",  # END OF MEDIUM
    "\u001a": "",  # SUBSTITUTE
    "\u001b": "",  # ESCAPE
    "\u001e": "",  # INFORMATION SEPARATOR TWO (record separator)
    "\u001f": "",  # INFORMATION SEPARATOR ONE (unit separator)
    # \r -> remove it
    "\r": "",
    # Strange parantheses - change for normal:
    "\x1c": "(",
    "\x1d": ")",
    # Some ff from tex:
    "\u0013\u0010": "\u00ed",
    "\x0b": "ff",
    # fi from tex:
    "\x0c": "fi",
    # ligatures from TeX:
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    # Superscripts from TeX
    "\u2212": "-",
    "\u2013": "-",
    # Word style speech marks:
    "\u201c ": '"',
    "\u201d": '"',
    "\u201c": '"',
    # pdftotext has problems with umlaut and prints it as diaeresis
    # followed by a letter:correct it
    # (Optional space between char and letter - fixes broken
    # line examples)
    "\u00a8 a": "\u00e4",
    "\u00a8 e": "\u00eb",
    "\u00a8 i": "\u00ef",
    "\u00a8 o": "\u00f6",
    "\u00a8 u": "\u00fc",
    "\u00a8 y": "\u00ff",
    "\u00a8 A": "\u00c4",
    "\u00a8 E": "\u00cb",
    "\u00a8 I": "\u00cf",
    "\u00a8 O": "\u00d6",
    "\u00a8 U": "\u00dc",
    "\u00a8 Y": "\u0178",
    "\xa8a": "\u00e4",
    "\xa8e": "\u00eb",
    "\xa8i": "\u00ef",
    "\xa8o": "\u00f6",
    "\xa8u": "\u00fc",
    "\xa8y": "\u00ff",
    "\xa8A": "\u00c4",
    "\xa8E": "\u00cb",
    "\xa8I": "\u00cf",
    "\xa8O": "\u00d6",
    "\xa8U": "\u00dc",
    "\xa8Y": "\u0178",
    # More umlaut mess to correct:
    "\x7fa": "\u00e4",
    "\x7fe": "\u00eb",
    "\x7fi": "\u00ef",
    "\x7fo": "\u00f6",
    "\x7fu": "\u00fc",
    "\x7fy": "\u00ff",
    "\x7fA": "\u00c4",
    "\x7fE": "\u00cb",
    "\x7fI": "\u00cf",
    "\x7fO": "\u00d6",
    "\x7fU": "\u00dc",
    "\x7fY": "\u0178",
    "\x7f a": "\u00e4",
    "\x7f e": "\u00eb",
    "\x7f i": "\u00ef",
    "\x7f o": "\u00f6",
    "\x7f u": "\u00fc",
    "\x7f y": "\u00ff",
    "\x7f A": "\u00c4",
    "\x7f E": "\u00cb",
    "\x7f I": "\u00cf",
    "\x7f O": "\u00d6",
    "\x7f U": "\u00dc",
    "\x7f Y": "\u0178",
    # pdftotext: fix accute accent:
    "\x13a": "\u00e1",
    "\x13e": "\u00e9",
    "\x13i": "\u00ed",
    "\x13o": "\u00f3",
    "\x13u": "\u00fa",
    "\x13y": "\u00fd",
    "\x13A": "\u00c1",
    "\x13E": "\u00c9",
    "\x13I": "\u00cd",
    "\x13ı": "\u00ed",  # Lower case turkish 'i' (dotless i)
    "\x13O": "\u00d3",
    "\x13U": "\u00da",
    "\x13Y": "\u00dd",
    "\x13 a": "\u00e1",
    "\x13 e": "\u00e9",
    "\x13 i": "\u00ed",
    "\x13 o": "\u00f3",
    "\x13 u": "\u00fa",
    "\x13 y": "\u00fd",
    "\x13 A": "\u00c1",
    "\x13 E": "\u00c9",
    "\x13 I": "\u00cd",
    "\x13 ı": "\u00ed",
    "\x13 O": "\u00d3",
    "\x13 U": "\u00da",
    "\x13 Y": "\u00dd",
    "\u00b4 a": "\u00e1",
    "\u00b4 e": "\u00e9",
    "\u00b4 i": "\u00ed",
    "\u00b4 o": "\u00f3",
    "\u00b4 u": "\u00fa",
    "\u00b4 y": "\u00fd",
    "\u00b4 A": "\u00c1",
    "\u00b4 E": "\u00c9",
    "\u00b4 I": "\u00cd",
    "\u00b4 ı": "\u00ed",
    "\u00b4 O": "\u00d3",
    "\u00b4 U": "\u00da",
    "\u00b4 Y": "\u00dd",
    "\u00b4a": "\u00e1",
    "\u00b4e": "\u00e9",
    "\u00b4i": "\u00ed",
    "\u00b4o": "\u00f3",
    "\u00b4u": "\u00fa",
    "\u00b4y": "\u00fd",
    "\u00b4A": "\u00c1",
    "\u00b4E": "\u00c9",
    "\u00b4I": "\u00cd",
    "\u00b4ı": "\u00ed",
    "\u00b4O": "\u00d3",
    "\u00b4U": "\u00da",
    "\u00b4Y": "\u00dd",
    # pdftotext: fix grave accent:
    "\u0060 a": "\u00e0",
    "\u0060 e": "\u00e8",
    "\u0060 i": "\u00ec",
    "\u0060 o": "\u00f2",
    "\u0060 u": "\u00f9",
    "\u0060 A": "\u00c0",
    "\u0060 E": "\u00c8",
    "\u0060 I": "\u00cc",
    "\u0060 O": "\u00d2",
    "\u0060 U": "\u00d9",
    "\u0060a": "\u00e0",
    "\u0060e": "\u00e8",
    "\u0060i": "\u00ec",
    "\u0060o": "\u00f2",
    "\u0060u": "\u00f9",
    "\u0060A": "\u00c0",
    "\u0060E": "\u00c8",
    "\u0060I": "\u00cc",
    "\u0060O": "\u00d2",
    "\u0060U": "\u00d9",
    "a´": "á",
    "i´": "í",
    "e´": "é",
    "u´": "ú",
    "o´": "ó",
    # \02C7 : caron
    "\u02c7C": "\u010c",
    "\u02c7c": "\u010d",
    "\u02c7S": "\u0160",
    "\u02c7s": "\u0161",
    "\u02c7Z": "\u017d",
    "\u02c7z": "\u017e",
    # \027 : aa (a with ring above)
    "\u02daa": "\u00e5",
    "\u02daA": "\u00c5",
    # \030 : cedilla
    "\u0327c": "\u00e7",
    "\u0327C": "\u00c7",
    "¸c": "ç",
    # \02DC : tilde
    "\u02dcn": "\u00f1",
    "\u02dcN": "\u00d1",
    "\u02dco": "\u00f5",
    "\u02dcO": "\u00d5",
    "\u02dca": "\u00e3",
    "\u02dcA": "\u00c3",
    "\u02dcs": "\u0303s",  # Combining tilde with 's'
    # Circumflex accent (caret accent)
    "aˆ": "â",
    "iˆ": "î",
    "eˆ": "ê",
    "uˆ": "û",
    "oˆ": "ô",
    "ˆa": "â",
    "ˆi": "î",
    "ˆe": "ê",
    "ˆu": "û",
    "ˆo": "ô",
}

UNDESIRABLE_STRING_REPLACEMENTS = [
    ("\u201c ", '"'),
]


def replace_undesirable_characters(line):
    """Replace certain bad characters in a text line.

    :param line: (string) the text line in which bad characters are to
                 be replaced.
    :return: (string) the text line after the bad characters have been
                      replaced.
    """
    # These are separate because we want a particular order
    for bad_string, replacement in UNDESIRABLE_STRING_REPLACEMENTS:
        line = line.replace(bad_string, replacement)

    for bad_char, replacement in iteritems(UNDESIRABLE_CHAR_REPLACEMENTS):
        line = line.replace(bad_char, replacement)

    return line


def _replace_greek_characters(line):
    """Replace greek characters in a string."""
    for greek_char, replacement in iteritems(_GREEK_REPLACEMENTS):
        try:
            line = line.replace(greek_char, replacement)
        except UnicodeDecodeError:
            logger.exception("Unicode decoding error.")
            return ""
    return line
