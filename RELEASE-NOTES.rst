===========================
 Invenio-Classifier v1.0.0
===========================

Incompatible changes
--------------------

- Changes module to be compatible with Invenio 3.

Bug fixes
---------

- Fixes a crash when trying to discover a taxonomy when
  CLASSIFIER_WORKDIR is set to None.
- Updates minimum dependencies of Invenio packages to newer versions.
- Removes a bug in bibclassify_keyword_analyzer.py. If a combination
  is found via a synonym or regexp it is no longer thrown away just
  because the components of the combination are not found in the text.
- Adds missing `invenio_base` dependency.

Installation
------------

   $ pip install invenio-classifier==0.1.0

Documentation
-------------

   http://invenio-classifier.readthedocs.org/en/v0.1.0

Happy hacking and thanks for flying Invenio-Classifier.

| Inspirehep Development Team
|   Email: admin@inspirehep.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware-contrib/invenio-classifier
|   URL: http://inveniosoftware.org
