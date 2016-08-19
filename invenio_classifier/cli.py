# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Perform classifier operations such as extracting keywords from PDF."""

from __future__ import absolute_import, print_function

import os
import sys

import click
from flask import current_app
from flask.cli import with_appcontext

from .api import get_keywords_from_local_file


@click.group()
def classifier():
    """Classifier commands."""


@classifier.command()
@click.option('-f', '--filepath',
              help='extract keywords from this file.')
@click.option('-k', '--taxonomy',
              help='the taxonomy file to use.')
@click.option('-o', '--output-mode', default="text",
              help='choose output format (text, dict, raw, html, marcxml).')
@click.option('-n', '--output-limit', default=20,
              help='the limit of keywords to display.')
@click.option('-s', '--spires', is_flag=True,
              help='outputs keywords in the SPIRES format.')
@click.option('-m', '--match-mode', default="full",
              help='choose full or partial searching mode.')
@click.option('-d', '--detect-author-keywords', is_flag=True,
              help='detect keywords that are from the authors.')
@click.option('-e', '--extract-acronyms', is_flag=True,
              help='outputs a list of acronyms and expansions found.')
@click.option('--rebuild-cache', is_flag=True,
              help='ignores the existing cache and regenerates it')
@click.option('-r', '--only-core-tags', is_flag=True,
              help='keep only CORE single and composite keywords.')
@click.option('--no-cache', is_flag=True,
              help='do not cache the taxonomy')
@with_appcontext
def extract(filepath, taxonomy, output_mode, output_limit,
            spires, match_mode, detect_author_keywords, extract_acronyms,
            rebuild_cache, only_core_tags, no_cache):
    """Run keyword extraction on given PDF file for given taxonomy."""
    if not filepath or not taxonomy:
        print("No PDF file or taxonomy given!", file=sys.stderr)
        sys.exit(0)

    click.echo(
        ">>> Going extract keywords from {0} as '{1}'...".format(
            filepath, output_mode
        )
    )
    if not os.path.isfile(filepath):
        click.echo(
            "Path to non-existing file\n",
        )
        sys.exit(1)

    result = get_keywords_from_local_file(
        local_file=filepath,
        taxonomy_name=taxonomy,
        output_mode=output_mode,
        output_limit=output_limit,
        spires=spires,
        match_mode=match_mode,
        no_cache=no_cache,
        with_author_keywords=detect_author_keywords,
        rebuild_cache=rebuild_cache,
        only_core_tags=only_core_tags,
        extract_acronyms=extract_acronyms
    )
    click.echo(result)
