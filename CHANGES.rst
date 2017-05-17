..
    This file is part of Invenio.
    Copyright (C) 2015 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 1.1.0 (release 2017-05-17)
----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Changes dict export format for author keywords, into an improved and semantic
  way.
- Renames keys in dict export to be lower case and separated by `_`.

Bug fixes
~~~~~~~~~

- Drop trailing dots in author keywords.

Version 1.0.1 (release 2017-01-11)
----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Changes module to be compatible with Invenio 3.

Bug fixes
~~~~~~~~~

- Fixes a crash when trying to discover a taxonomy when
  CLASSIFIER_WORKDIR is set to None.
- Updates minimum dependencies of Invenio packages to newer versions.
- Removes a bug in bibclassify_keyword_analyzer.py. If a combination
  is found via a synonym or regexp it is no longer thrown away just
  because the components of the combination are not found in the text.
- Adds missing `invenio_base` dependency.

Version 0.1.0 (release 2015-08-19)
----------------------------------

- Initial public release.
