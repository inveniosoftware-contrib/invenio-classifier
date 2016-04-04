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

import re

from flask import current_app
from six import iteritems

from .find import find_end_of_reference_section, find_reference_section

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
        for name in ("c", "muon", "s", "B", "D", "K", "Lambda",
                     "Mu", "Omega", "Pi", "Sigma", "Tau", "W", "Xi")
    ]

    # Particles followed by numbers
    washing_regex += [
        (re.compile(r"(\W%s) ([0-9]\W)" % name), r"\1\2")
        for name in ("a", "b", "c", "f", "h", "s", "B", "D", "H",
                     "K", "L", "Phi", "Pi", "Psi", "Rho", "Stor", "UA",
                     "Xi", "Z")
    ]
    washing_regex += [(re.compile(r"(\W%s) ?\( ?([0-9]+) ?\)[A-Z]?" % name),
                       r"\1(\2)")
                      for name in ("CP", "E", "G", "O", "S", "SL", "SO",
                                   "Spin", "SU", "U", "W", "Z")]

    # Particles with '
    washing_regex += [(re.compile(r"(\W%s) ('\W)" % name), r"\1\2")
                      for name in ("Eta", "W", "Z")]

    # Particles with (N)
    washing_regex += [(re.compile(r"(\W%s) ?\( ?N ?\)[A-Z]?" % name), r"\1(N)")
                      for name in ("CP", "GL", "O", "SL", "SO", "Sp", "Spin",
                                   "SU", "U", "W", "Z")]

    # All names followed by ([0-9]{3,4})
    washing_regex.append((re.compile(r"([A-Za-z]) (\([0-9]{3,4}\)\+?)\s"),
                          r"\1\2 "))

    # Some weird names followed by ([0-9]{3,4})
    washing_regex += [(re.compile(r"\(%s\) (\([0-9]{3,4}\))" % name),
                       r"\1\2 ")
                      for name in ("a0", "Ds1", "Ds2", "K\*")]

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
        fulltext = regex.sub(replacement, fulltext)

    return fulltext


def cut_references(text_lines):
    """Return the text lines with the references cut."""
    ref_sect_start = find_reference_section(text_lines)
    if ref_sect_start is not None:
        start = ref_sect_start["start_line"]
        end = find_end_of_reference_section(text_lines, start,
                                            ref_sect_start["marker"],
                                            ref_sect_start["marker_pattern"])
        del text_lines[start:end + 1]
    else:
        current_app.logger.warning("Found no references to remove.")
        return text_lines

    return text_lines


_GREEK_REPLACEMENTS = {
    u'\u00AF': u' ',
    u'\u00B5': u' Mu ',
    u'\u00D7': u' x ',
    u'\u0391': u' Alpha ',
    u'\u0392': u' Beta ',
    u'\u0393': u' Gamma ',
    u'\u0394': u' Delta ',
    u'\u0395': u' Epsilon ',
    u'\u0396': u' Zeta ',
    u'\u0397': u' Eta ',
    u'\u0398': u' Theta ',
    u'\u0399': u' Iota ',
    u'\u039A': u' Kappa ',
    u'\u039B': u' Lambda ',
    u'\u039C': u' Mu ',
    u'\u039D': u' Nu ',
    u'\u039E': u' Xi ',
    u'\u039F': u' Omicron ',
    u'\u03A0': u' Pi ',
    u'\u03A1': u' Rho ',
    u'\u03A3': u' Sigma ',
    u'\u03A4': u' Tau ',
    u'\u03A5': u' Upsilon ',
    u'\u03A6': u' Phi ',
    u'\u03A7': u' Chi ',
    u'\u03A8': u' Psi ',
    u'\u03A9': u' Omega ',
    u'\u03B1': u' Alpha ',
    u'\u03B2': u' Beta ',
    u'\u03B3': u' Gamma ',
    u'\u03B4': u' Delta ',
    u'\u03B5': u' Epsilon ',
    u'\u03B6': u' Zeta ',
    u'\u03B7': u' Eta ',
    u'\u03B8': u' Theta ',
    u'\u03B9': u' Iota ',
    u'\u03BA': u' Kappa ',
    u'\u03BB': u' Lambda ',
    u'\u03BC': u' Mu ',
    u'\u03BD': u' Nu ',
    u'\u03BE': u' Xi ',
    u'\u03BF': u' Omicron ',
    u'\u03C0': u' Pi ',
    u'\u03C1': u' Rho ',
    u'\uC3C2': u' Sigma ',
    u'\u03C3': u' Sigma ',
    u'\u03C4': u' Tau ',
    u'\u03C5': u' Upsilon ',
    u'\u03C6': u' Phi ',
    u'\u03C7': u' Chi ',
    u'\u03C8': u' Psi ',
    u'\u03C9': u' Omega ',
    u'\u03CA': u' Iota ',
    u'\u03CB': u' Upsilon ',
    u'\u03CC': u' Omicron ',
    u'\u03CD': u' Upsilon ',
    u'\u03CE': u' Omega ',
    u'\u03CF': u' Kai ',
    u'\u03D0': u' Beta ',
    u'\u03D1': u' Theta ',
    u'\u03D2': u' Upsilon ',
    u'\u03D3': u' Upsilon ',
    u'\u03D4': u' Upsilon ',
    u'\u03D5': u' Phi ',
    u'\u03D6': u' Pi ',
    u'\u03D7': u' Kai ',
    u'\u03D8': u' Koppa ',
    u'\u03D9': u' Koppa ',
    u'\u03DA': u' Stigma ',
    u'\u03DB': u' Stigma ',
    u'\u03DC': u' Digamma ',
    u'\u03DD': u' Digamma ',
    u'\u03DE': u' Koppa ',
    u'\u03DF': u' Koppa ',
    u'\u03E0': u' Sampi ',
    u'\u03E1': u' Sampi ',
    u'\u03D1': u' Theta ',
    u'\u03D5': u' Phi ',
    u'\u2010': u'-',
    u'\u2011': u'-',
    u'\u2012': u'-',
    u'\u2013': u'-',
    u'\u2014': u'-',
    u'\u2015': u'-',
    u'\u2019': u"'",
    u'\u2032': u"'",
    u'\u2126': u' Omega ',
    u'\u2206': u' Delta ',
    u'\u2212': u'-',
    u'\u2215': u"/",
    u'\u2216': u"\\",
    u'\u2217': u"*",
    u'\u221D': u' Alpha ',
}

# a dictionary of undesirable characters and their replacements:
UNDESIRABLE_CHAR_REPLACEMENTS = {
    # Control characters not allowed in XML:
    u'\u2028': u"",
    u'\u2029': u"",
    u'\u202A': u"",
    u'\u202B': u"",
    u'\u202C': u"",
    u'\u202D': u"",
    u'\u202E': u"",
    u'\u206A': u"",
    u'\u206B': u"",
    u'\u206C': u"",
    u'\u206D': u"",
    u'\u206E': u"",
    u'\u206F': u"",
    u'\uFFF9': u"",
    u'\uFFFA': u"",
    u'\uFFFB': u"",
    u'\uFFFC': u"",
    u'\uFEFF': u"",
    # Remove the result of a bad UTF-8 character
    u'\uFFFF': u"",
    # Language Tag Code Points:
    u"\U000E0000": u"",
    u"\U000E0001": u"",
    u"\U000E0002": u"",
    u"\U000E0003": u"",
    u"\U000E0004": u"",
    u"\U000E0005": u"",
    u"\U000E0006": u"",
    u"\U000E0007": u"",
    u"\U000E0008": u"",
    u"\U000E0009": u"",
    u"\U000E000A": u"",
    u"\U000E000B": u"",
    u"\U000E000C": u"",
    u"\U000E000D": u"",
    u"\U000E000E": u"",
    u"\U000E000F": u"",
    u"\U000E0010": u"",
    u"\U000E0011": u"",
    u"\U000E0012": u"",
    u"\U000E0013": u"",
    u"\U000E0014": u"",
    u"\U000E0015": u"",
    u"\U000E0016": u"",
    u"\U000E0017": u"",
    u"\U000E0018": u"",
    u"\U000E0019": u"",
    u"\U000E001A": u"",
    u"\U000E001B": u"",
    u"\U000E001C": u"",
    u"\U000E001D": u"",
    u"\U000E001E": u"",
    u"\U000E001F": u"",
    u"\U000E0020": u"",
    u"\U000E0021": u"",
    u"\U000E0022": u"",
    u"\U000E0023": u"",
    u"\U000E0024": u"",
    u"\U000E0025": u"",
    u"\U000E0026": u"",
    u"\U000E0027": u"",
    u"\U000E0028": u"",
    u"\U000E0029": u"",
    u"\U000E002A": u"",
    u"\U000E002B": u"",
    u"\U000E002C": u"",
    u"\U000E002D": u"",
    u"\U000E002E": u"",
    u"\U000E002F": u"",
    u"\U000E0030": u"",
    u"\U000E0031": u"",
    u"\U000E0032": u"",
    u"\U000E0033": u"",
    u"\U000E0034": u"",
    u"\U000E0035": u"",
    u"\U000E0036": u"",
    u"\U000E0037": u"",
    u"\U000E0038": u"",
    u"\U000E0039": u"",
    u"\U000E003A": u"",
    u"\U000E003B": u"",
    u"\U000E003C": u"",
    u"\U000E003D": u"",
    u"\U000E003E": u"",
    u"\U000E003F": u"",
    u"\U000E0040": u"",
    u"\U000E0041": u"",
    u"\U000E0042": u"",
    u"\U000E0043": u"",
    u"\U000E0044": u"",
    u"\U000E0045": u"",
    u"\U000E0046": u"",
    u"\U000E0047": u"",
    u"\U000E0048": u"",
    u"\U000E0049": u"",
    u"\U000E004A": u"",
    u"\U000E004B": u"",
    u"\U000E004C": u"",
    u"\U000E004D": u"",
    u"\U000E004E": u"",
    u"\U000E004F": u"",
    u"\U000E0050": u"",
    u"\U000E0051": u"",
    u"\U000E0052": u"",
    u"\U000E0053": u"",
    u"\U000E0054": u"",
    u"\U000E0055": u"",
    u"\U000E0056": u"",
    u"\U000E0057": u"",
    u"\U000E0058": u"",
    u"\U000E0059": u"",
    u"\U000E005A": u"",
    u"\U000E005B": u"",
    u"\U000E005C": u"",
    u"\U000E005D": u"",
    u"\U000E005E": u"",
    u"\U000E005F": u"",
    u"\U000E0060": u"",
    u"\U000E0061": u"",
    u"\U000E0062": u"",
    u"\U000E0063": u"",
    u"\U000E0064": u"",
    u"\U000E0065": u"",
    u"\U000E0066": u"",
    u"\U000E0067": u"",
    u"\U000E0068": u"",
    u"\U000E0069": u"",
    u"\U000E006A": u"",
    u"\U000E006B": u"",
    u"\U000E006C": u"",
    u"\U000E006D": u"",
    u"\U000E006E": u"",
    u"\U000E006F": u"",
    u"\U000E0070": u"",
    u"\U000E0071": u"",
    u"\U000E0072": u"",
    u"\U000E0073": u"",
    u"\U000E0074": u"",
    u"\U000E0075": u"",
    u"\U000E0076": u"",
    u"\U000E0077": u"",
    u"\U000E0078": u"",
    u"\U000E0079": u"",
    u"\U000E007A": u"",
    u"\U000E007B": u"",
    u"\U000E007C": u"",
    u"\U000E007D": u"",
    u"\U000E007E": u"",
    u"\U000E007F": u"",
    # Musical Notation Scoping
    u"\U0001D173": u"",
    u"\U0001D174": u"",
    u"\U0001D175": u"",
    u"\U0001D176": u"",
    u"\U0001D177": u"",
    u"\U0001D178": u"",
    u"\U0001D179": u"",
    u"\U0001D17A": u"",
    u'\u0000': u"",  # NULL
    u'\u0001': u"",  # START OF HEADING
    # START OF TEXT & END OF TEXT:
    u'\u0002': u"",
    u'\u0003': u"",
    u'\u0004': u"",  # END OF TRANSMISSION
    # ENQ and ACK
    u'\u0005': u"",
    u'\u0006': u"",
    u'\u0007': u"",  # BELL
    u'\u0008': u"",  # BACKSPACE
    # SHIFT-IN & SHIFT-OUT
    u'\u000E': u"",
    u'\u000F': u"",
    # Other controls:
    u'\u0010': u"",  # DATA LINK ESCAPE
    u'\u0011': u"",  # DEVICE CONTROL ONE
    u'\u0012': u"",  # DEVICE CONTROL TWO
    u'\u0013': u"",  # DEVICE CONTROL THREE
    u'\u0014': u"",  # DEVICE CONTROL FOUR
    u'\u0015': u"",  # NEGATIVE ACK
    u'\u0016': u"",  # SYNCRONOUS IDLE
    u'\u0017': u"",  # END OF TRANSMISSION BLOCK
    u'\u0018': u"",  # CANCEL
    u'\u0019': u"",  # END OF MEDIUM
    u'\u001A': u"",  # SUBSTITUTE
    u'\u001B': u"",  # ESCAPE
    u'\u001C': u"",  # INFORMATION SEPARATOR FOUR (file separator)
    u'\u001D': u"",  # INFORMATION SEPARATOR THREE (group separator)
    u'\u001E': u"",  # INFORMATION SEPARATOR TWO (record separator)
    u'\u001F': u"",  # INFORMATION SEPARATOR ONE (unit separator)
    # \r -> remove it
    u'\r': u"",
    # Strange parantheses - change for normal:
    u'\x1c': u'(',
    u'\x1d': u')',
    # Some ff from tex:
    u'\u0013\u0010': u'\u00ED',
    u'\x0b': u'ff',
    # fi from tex:
    u'\x0c': u'fi',
    # ligatures from TeX:
    u'\ufb00': u'ff',
    u'\ufb01': u'fi',
    u'\ufb02': u'fl',
    u'\ufb03': u'ffi',
    u'\ufb04': u'ffl',
    # Superscripts from TeX
    u'\u2212': u'-',
    u'\u2013': u'-',
    # Word style speech marks:
    u'\u201c ': u'"',
    u'\u201d': u'"',
    u'\u201c': u'"',
    # pdftotext has problems with umlaut and prints it as diaeresis
    # followed by a letter:correct it
    # (Optional space between char and letter - fixes broken
    # line examples)
    u'\u00A8 a': u'\u00E4',
    u'\u00A8 e': u'\u00EB',
    u'\u00A8 i': u'\u00EF',
    u'\u00A8 o': u'\u00F6',
    u'\u00A8 u': u'\u00FC',
    u'\u00A8 y': u'\u00FF',
    u'\u00A8 A': u'\u00C4',
    u'\u00A8 E': u'\u00CB',
    u'\u00A8 I': u'\u00CF',
    u'\u00A8 O': u'\u00D6',
    u'\u00A8 U': u'\u00DC',
    u'\u00A8 Y': u'\u0178',
    u'\xA8a': u'\u00E4',
    u'\xA8e': u'\u00EB',
    u'\xA8i': u'\u00EF',
    u'\xA8o': u'\u00F6',
    u'\xA8u': u'\u00FC',
    u'\xA8y': u'\u00FF',
    u'\xA8A': u'\u00C4',
    u'\xA8E': u'\u00CB',
    u'\xA8I': u'\u00CF',
    u'\xA8O': u'\u00D6',
    u'\xA8U': u'\u00DC',
    u'\xA8Y': u'\u0178',
    # More umlaut mess to correct:
    u'\x7fa': u'\u00E4',
    u'\x7fe': u'\u00EB',
    u'\x7fi': u'\u00EF',
    u'\x7fo': u'\u00F6',
    u'\x7fu': u'\u00FC',
    u'\x7fy': u'\u00FF',
    u'\x7fA': u'\u00C4',
    u'\x7fE': u'\u00CB',
    u'\x7fI': u'\u00CF',
    u'\x7fO': u'\u00D6',
    u'\x7fU': u'\u00DC',
    u'\x7fY': u'\u0178',
    u'\x7f a': u'\u00E4',
    u'\x7f e': u'\u00EB',
    u'\x7f i': u'\u00EF',
    u'\x7f o': u'\u00F6',
    u'\x7f u': u'\u00FC',
    u'\x7f y': u'\u00FF',
    u'\x7f A': u'\u00C4',
    u'\x7f E': u'\u00CB',
    u'\x7f I': u'\u00CF',
    u'\x7f O': u'\u00D6',
    u'\x7f U': u'\u00DC',
    u'\x7f Y': u'\u0178',
    # pdftotext: fix accute accent:
    u'\x13a': u'\u00E1',
    u'\x13e': u'\u00E9',
    u'\x13i': u'\u00ED',
    u'\x13o': u'\u00F3',
    u'\x13u': u'\u00FA',
    u'\x13y': u'\u00FD',
    u'\x13A': u'\u00C1',
    u'\x13E': u'\u00C9',
    u'\x13I': u'\u00CD',
    u'\x13ı': u'\u00ED',  # Lower case turkish 'i' (dotless i)
    u'\x13O': u'\u00D3',
    u'\x13U': u'\u00DA',
    u'\x13Y': u'\u00DD',
    u'\x13 a': u'\u00E1',
    u'\x13 e': u'\u00E9',
    u'\x13 i': u'\u00ED',
    u'\x13 o': u'\u00F3',
    u'\x13 u': u'\u00FA',
    u'\x13 y': u'\u00FD',
    u'\x13 A': u'\u00C1',
    u'\x13 E': u'\u00C9',
    u'\x13 I': u'\u00CD',
    u'\x13 ı': u'\u00ED',
    u'\x13 O': u'\u00D3',
    u'\x13 U': u'\u00DA',
    u'\x13 Y': u'\u00DD',
    u'\u00B4 a': u'\u00E1',
    u'\u00B4 e': u'\u00E9',
    u'\u00B4 i': u'\u00ED',
    u'\u00B4 o': u'\u00F3',
    u'\u00B4 u': u'\u00FA',
    u'\u00B4 y': u'\u00FD',
    u'\u00B4 A': u'\u00C1',
    u'\u00B4 E': u'\u00C9',
    u'\u00B4 I': u'\u00CD',
    u'\u00B4 ı': u'\u00ED',
    u'\u00B4 O': u'\u00D3',
    u'\u00B4 U': u'\u00DA',
    u'\u00B4 Y': u'\u00DD',
    u'\u00B4a': u'\u00E1',
    u'\u00B4e': u'\u00E9',
    u'\u00B4i': u'\u00ED',
    u'\u00B4o': u'\u00F3',
    u'\u00B4u': u'\u00FA',
    u'\u00B4y': u'\u00FD',
    u'\u00B4A': u'\u00C1',
    u'\u00B4E': u'\u00C9',
    u'\u00B4I': u'\u00CD',
    u'\u00B4ı': u'\u00ED',
    u'\u00B4O': u'\u00D3',
    u'\u00B4U': u'\u00DA',
    u'\u00B4Y': u'\u00DD',
    # pdftotext: fix grave accent:
    u'\u0060 a': u'\u00E0',
    u'\u0060 e': u'\u00E8',
    u'\u0060 i': u'\u00EC',
    u'\u0060 o': u'\u00F2',
    u'\u0060 u': u'\u00F9',
    u'\u0060 A': u'\u00C0',
    u'\u0060 E': u'\u00C8',
    u'\u0060 I': u'\u00CC',
    u'\u0060 O': u'\u00D2',
    u'\u0060 U': u'\u00D9',
    u'\u0060a': u'\u00E0',
    u'\u0060e': u'\u00E8',
    u'\u0060i': u'\u00EC',
    u'\u0060o': u'\u00F2',
    u'\u0060u': u'\u00F9',
    u'\u0060A': u'\u00C0',
    u'\u0060E': u'\u00C8',
    u'\u0060I': u'\u00CC',
    u'\u0060O': u'\u00D2',
    u'\u0060U': u'\u00D9',
    u'a´': u'á',
    u'i´': u'í',
    u'e´': u'é',
    u'u´': u'ú',
    u'o´': u'ó',
    # \02C7 : caron
    u'\u02C7C': u'\u010C',
    u'\u02C7c': u'\u010D',
    u'\u02C7S': u'\u0160',
    u'\u02C7s': u'\u0161',
    u'\u02C7Z': u'\u017D',
    u'\u02C7z': u'\u017E',
    # \027 : aa (a with ring above)
    u'\u02DAa': u'\u00E5',
    u'\u02DAA': u'\u00C5',
    # \030 : cedilla
    u'\u0327c': u'\u00E7',
    u'\u0327C': u'\u00C7',
    u'¸c': u'ç',
    # \02DC : tilde
    u'\u02DCn': u'\u00F1',
    u'\u02DCN': u'\u00D1',
    u'\u02DCo': u'\u00F5',
    u'\u02DCO': u'\u00D5',
    u'\u02DCa': u'\u00E3',
    u'\u02DCA': u'\u00C3',
    u'\u02DCs': u'\u0303s',  # Combining tilde with 's'
    # Circumflex accent (caret accent)
    u'aˆ': u'â',
    u'iˆ': u'î',
    u'eˆ': u'ê',
    u'uˆ': u'û',
    u'oˆ': u'ô',
    u'ˆa': u'â',
    u'ˆi': u'î',
    u'ˆe': u'ê',
    u'ˆu': u'û',
    u'ˆo': u'ô',
}

UNDESIRABLE_STRING_REPLACEMENTS = [
    (u'\u201c ', '"'),
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
            current_app.logger.exception("Unicode decoding error.")
            return ""
    return line
