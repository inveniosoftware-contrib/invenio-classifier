# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2010, 2011, 2013, 2014, 2015, 2016 CERN.
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

"""Test suite for classifier module."""

from __future__ import absolute_import, print_function

import os
import shutil
import stat
import time

import pytest

from invenio_classifier import get_keywords_from_local_file, \
    get_keywords_from_text
from invenio_classifier.errors import TaxonomyError


def test_keywords(app, demo_taxonomy, demo_text):
    """Test keyword extraction from text."""
    with app.app_context():
        out = get_keywords_from_text(
            text_lines=[demo_text],
            taxonomy_name=demo_taxonomy,
            output_mode="dict"
        )
        output = out.get("complete_output")
        single_keywords = output.get("single_keywords", [])

        assert len(single_keywords) == 3
        assert ("aberration", 2) in single_keywords

        core_keywords = output.get("core_keywords", [])

        assert len(core_keywords) == 2
        assert ("supersymmetry", 1) in core_keywords


def test_taxonomy_error(app, demo_text):
    """Test passing non existing taxonomy."""
    with app.app_context():
        with pytest.raises(TaxonomyError):
            out = get_keywords_from_text(
                text_lines=[demo_text],
                taxonomy_name="foo",
                output_mode="dict"
            )


def test_file_extration(app, demo_pdf_file, demo_taxonomy):
    """Test extracting keywords from PDF."""
    with app.app_context():
        out = get_keywords_from_local_file(
            demo_pdf_file,
            taxonomy_name=demo_taxonomy,
            output_mode="dict"
        )
        output = out.get("complete_output")
        single_keywords = output.get("single_keywords", [])

        assert len(single_keywords) == 4
        assert ("gauge field theory Yang-Mills", 9) in single_keywords

        core_keywords = output.get("core_keywords", [])

        assert len(core_keywords) == 3
        assert ("Yang-Mills", 12) in core_keywords


def test_author_keywords(app, demo_pdf_file_with_author_keywords,
                         demo_taxonomy):
    """Test extracting author keywords from PDF."""
    with app.app_context():
        out = get_keywords_from_local_file(
            demo_pdf_file_with_author_keywords,
            taxonomy_name=demo_taxonomy,
            output_mode="dict",
            with_author_keywords=True
        )
        output = out.get("complete_output")
        author_keywords = output.get("author_keywords", [])

        assert len(author_keywords) == 4, output
        assert {'author_keyword': 'g-measure'} in author_keywords


def test_author_keywords(app, demo_pdf_file_with_funny_author_kw_sep,
                         demo_taxonomy):
    """Test extracting author keywords separated by '·'"""
    with app.app_context():
        out = get_keywords_from_local_file(
            demo_pdf_file_with_funny_author_kw_sep,
            taxonomy_name=demo_taxonomy,
            output_mode="dict",
            with_author_keywords=True
        )
        output = out.get("complete_output")
        author_keywords = output.get("author_keywords", [])

        assert len(author_keywords) == 4, output
        assert {'author_keyword': 'Depth cameras'} in author_keywords


def test_taxonomy_workdir(app, demo_text, demo_taxonomy):
    """Test grabbing taxonomy from the CLASSIFIER_WORKDIR."""
    app.config.update({"CLASSIFIER_WORKDIR": os.path.dirname(demo_taxonomy)})
    with app.app_context():
        out = get_keywords_from_text(
            text_lines=[demo_text],
            taxonomy_name="test.rdf",
            output_mode="dict"
        )
        output = out.get("complete_output")
        single_keywords = output.get("single_keywords", [])

        assert len(single_keywords) == 3
        assert ("aberration", 2) in single_keywords

        core_keywords = output.get("core_keywords", [])

        assert len(core_keywords) == 2
        assert ("supersymmetry", 1) in core_keywords


def test_rebuild_cache(app, demo_taxonomy):
    """Test rebuilding taxonomy cache."""
    from invenio_classifier.reader import (
        _get_ontology,
        _get_cache_path,
        get_regular_expressions
    )

    with app.app_context():
        info = _get_ontology(demo_taxonomy)

        assert info[0]
        cache = _get_cache_path(info[0])

        if os.path.exists(cache):
            ctime = os.stat(cache)[stat.ST_CTIME]
        else:
            ctime = -1

        time.sleep(0.5)  # sleep a bit for timing issues
        rex = get_regular_expressions(
            demo_taxonomy, rebuild=True)

        assert os.path.exists(cache)

        ntime = os.stat(cache)[stat.ST_CTIME]
        assert ntime > ctime

        assert len(rex[0]) + len(rex[1]) == 63


def test_cache_accessibility(app, demo_taxonomy):
    """Test taxonomy cache accessibility/writability."""
    from invenio_classifier.reader import (
        _get_ontology, get_regular_expressions, _get_cache_path
    )

    assert os.path.exists(demo_taxonomy)

    with app.app_context():
        # we will do tests with a copy of test taxonomy, in case anything goes
        # wrong...
        orig_name, orig_taxonomy_path, orig_taxonomy_url = _get_ontology(
            demo_taxonomy)

        demo_taxonomy = demo_taxonomy + '.copy.rdf'

        shutil.copy(orig_taxonomy_path, demo_taxonomy)

        dummy_name, demo_taxonomy, dummy_url = _get_ontology(demo_taxonomy)
        cache = _get_cache_path(demo_taxonomy)

        if os.path.exists(cache):
            os.remove(cache)

        get_regular_expressions(demo_taxonomy, rebuild=True, no_cache=False)

        assert os.path.exists(cache)

        # set cache unreadable
        os.chmod(cache, 000)

        with pytest.raises(TaxonomyError):
            get_regular_expressions(
                demo_taxonomy, rebuild=False, no_cache=False
            )

        # set cache unreadable and test writing
        os.chmod(cache, 000)

        with pytest.raises(TaxonomyError):
            get_regular_expressions(
                demo_taxonomy, rebuild=True, no_cache=False
            )

        # set cache readable and test writing
        os.chmod(cache, 600)

        with pytest.raises(TaxonomyError):
            get_regular_expressions(
                demo_taxonomy, rebuild=True, no_cache=False
            )

        # set cache writable only
        os.chmod(cache, 200)

        get_regular_expressions(
            demo_taxonomy, rebuild=True, no_cache=False)

        get_regular_expressions(
            demo_taxonomy, rebuild=False, no_cache=False)

        # set cache readable/writable but corrupted (must rebuild itself)
        os.chmod(cache, 600)
        os.remove(cache)
        open(cache, 'w').close()

        get_regular_expressions(
            demo_taxonomy, rebuild=False, no_cache=False)

        # set cache readable/writable but corrupted (must rebuild itself)
        open(cache, 'w').close()
        try:
            os.rename(demo_taxonomy, demo_taxonomy + 'x')
            open(demo_taxonomy, 'w').close()
            with pytest.raises(TaxonomyError):
                get_regular_expressions(
                    demo_taxonomy,
                    rebuild=False,
                    no_cache=False
                )
        finally:
            os.rename(demo_taxonomy + 'x', demo_taxonomy)

        # make cache ok, but corrupt source
        get_regular_expressions(
            demo_taxonomy, rebuild=True, no_cache=False)

        try:
            os.rename(demo_taxonomy, demo_taxonomy + 'x')
            open(demo_taxonomy, 'w').close()
            time.sleep(.1)
            # touch the taxonomy to be older
            os.utime(cache, (time.time() + 100, time.time() + 100))
            get_regular_expressions(
                demo_taxonomy, rebuild=False, no_cache=False)
        finally:
            os.rename(demo_taxonomy + 'x', demo_taxonomy)

        # make cache ok (but old), and corrupt source
        get_regular_expressions(
            demo_taxonomy, rebuild=True, no_cache=False)
        try:
            os.rename(demo_taxonomy, demo_taxonomy + 'x')
            open(demo_taxonomy, 'w').close()
            with pytest.raises(TaxonomyError):
                get_regular_expressions(
                    demo_taxonomy,
                    rebuild=False,
                    no_cache=False
                )
        finally:
            os.rename(demo_taxonomy + 'x', demo_taxonomy)

        name, demo_taxonomy, taxonomy_url = _get_ontology(demo_taxonomy)
        cache = _get_cache_path(name)
        os.remove(demo_taxonomy)
        os.remove(cache)
