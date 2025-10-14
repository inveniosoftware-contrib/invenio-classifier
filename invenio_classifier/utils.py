# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Contains utils for classifier."""

import re
import sys
import six
import time


def encode_for_xml(text, wash=False, xml_version="1.0", quote=False):
    """Encode special characters in a text so that it would be XML-compliant.

    :param text: text to encode
    :return: an encoded text
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    if quote:
        text = text.replace('"', "&quot;")
    if wash:
        text = wash_for_xml(text, xml_version=xml_version)
    return text


try:
    six.unichr(0x100000)
    RE_ALLOWED_XML_1_0_CHARS = re.compile(
        "[^\U00000009\U0000000a\U0000000d\U00000020-"
        "\U0000d7ff\U0000e000-\U0000fffd\U00010000-\U0010ffff]"
    )
    RE_ALLOWED_XML_1_1_CHARS = re.compile(
        "[^\U00000001-\U0000d7ff\U0000e000-\U0000fffd\U00010000-\U0010ffff]"
    )
except ValueError:
    # oops, we are running on a narrow UTF/UCS Python build,
    # so we have to limit the UTF/UCS char range:
    RE_ALLOWED_XML_1_0_CHARS = re.compile(
        "[^\U00000009\U0000000a\U0000000d\U00000020-" "\U0000d7ff\U0000e000-\U0000fffd]"
    )
    RE_ALLOWED_XML_1_1_CHARS = re.compile(
        "[^\U00000001-\U0000d7ff\U0000e000-\U0000fffd]"
    )


def wash_for_xml(text, xml_version="1.0"):
    """Remove any character which isn't a allowed characters for XML.

    The allowed characters depends on the version
    of XML.
        - XML 1.0:
            <http://www.w3.org/TR/REC-xml/#charsets>
        - XML 1.1:
            <http://www.w3.org/TR/xml11/#charsets>
    :param text: input string to wash.
    :param xml_version: version of the XML for which we wash the
        input. Value for this parameter can be '1.0' or '1.1'
    """
    if xml_version == "1.0":
        return RE_ALLOWED_XML_1_0_CHARS.sub("", six.text_type(text, "utf-8")).encode(
            "utf-8"
        )
    else:
        return RE_ALLOWED_XML_1_1_CHARS.sub("", six.text_type(text, "utf-8")).encode(
            "utf-8"
        )


def get_clock():
    if sys.version_info < (3, 3):
        return time.clock()
    return time.perf_counter()
