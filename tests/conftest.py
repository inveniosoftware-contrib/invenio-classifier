# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import tempfile

import pytest
from flask import Flask

from invenio_classifier import InvenioClassifier


@pytest.fixture()
def app():
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask(__name__, instance_path=instance_path)
    app.config.update(
        TESTING=True,
    )
    InvenioClassifier(app)
    return app


@pytest.fixture
def demo_taxonomy():
    """Return path to demo taxonomy file."""
    return os.path.join(
        os.path.dirname(__file__), 'data', 'taxonomies',
        'test.rdf'
    )


@pytest.fixture
def demo_pdf_file():
    """Return path to demo PDF file."""
    return os.path.join(
        os.path.dirname(__file__), 'data',
        '1603.08749.pdf'
    )


@pytest.fixture
def demo_pdf_file_with_funny_author_kw_sep():
    """Return path to demo PDF file."""
    return os.path.join(
        os.path.dirname(__file__), 'data',
        '1705.06516.pdf'
    )


@pytest.fixture
def demo_pdf_file_with_author_keywords():
    """Return path to demo PDF file with author keywords."""
    return os.path.join(
        os.path.dirname(__file__), 'data',
        '1705.03156.pdf'
    )


@pytest.fixture
def demo_text():
    """Return sample text to extract keywords from."""
    return """
We study the three-dimensional effective action obtained by reducing
eleven-dimensional supergravity with higher-derivative terms on a background
solution including a warp-factor, an eight-dimensional compact manifold, and
fluxes. The dynamical fields are K\"ahler deformations and vectors from the
M-theory three-form. We show that the potential is only induced by fluxes and
the naive contributions obtained from higher-curvature terms on a Calabi-Yau
background aberration once the back-reaction to the full solution is taken
into account. For the resulting three-dimensional action we analyse
the K\"ahler potential and complex coordinates and show compatibility
with N=2 supersymmetry. We argue that the higher-order result is also
compatible with a no-scale aberration. We find that the complex
coordinates should be formulated as divisor integrals for which a
non-trivial interplay between the warp-factor terms and the
higher-curvature terms allow a derivation of the moduli space metric.
This leads us to discuss higher-derivative corrections to the M5-brane
action.
"""
