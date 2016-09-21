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

====================
 Invenio-Classifier
====================

.. image:: https://img.shields.io/travis/inveniosoftware-contrib/invenio-classifier.svg
        :target: https://travis-ci.org/inveniosoftware-contrib/invenio-classifier

.. image:: https://img.shields.io/coveralls/inveniosoftware-contrib/invenio-classifier.svg
        :target: https://coveralls.io/r/inveniosoftware-contrib/invenio-classifier

.. image:: https://img.shields.io/github/tag/inveniosoftware-contrib/invenio-classifier.svg
        :target: https://github.com/inveniosoftware-contrib/invenio-classifier/releases

.. image:: https://img.shields.io/pypi/dm/invenio-classifier.svg
        :target: https://pypi.python.org/pypi/invenio-classifier

.. image:: https://img.shields.io/github/license/inveniosoftware-contrib/invenio-classifier.svg
        :target: https://github.com/inveniosoftware-contrib/invenio-classifier/blob/master/LICENSE


Invenio module for record classification.

* Free software: GPLv2 license
* Documentation: https://pythonhosted.org/invenio-classifier


Features
========

Classifier automatically extracts keywords from fulltext documents. The
automatic assignment of keywords to textual documents has clear benefits
in the digital library environment as it aids catalogization,
classification and retrieval of documents.

Keyword extraction is simple
============================

.. note:: Classifier requires Python `RDFLib <http://rdflib.net/>`__ in order
    to process the RDF/SKOS taxonomy.

In order to extract relevant keywords from a document ``fulltext.pdf``
based on a controlled vocabulary ``thesaurus.rdf``, you would run
Classifier as follows:

.. code-block:: shell

    ${INVENIO_WEB_INSTANCE} classifier extract -k thesaurus.rdf -f fulltext.pdf

Launching ``${INVENIO_WEB_INSTANCE} classifier --help`` shows the options available.

As an example, running classifier on document
`nucl-th/0204033 <http://cds.cern.ch/record/547024>`__ using the
high-energy physics RDF/SKOS taxonomy (``HEP.rdf``) would yield the
following results (based on the HEP taxonomy from October 10th 2008):

.. code-block:: text

    Input file: 0204033.pdf

    Author keywords:
    Dense matter
    Saturation
    Unstable nuclei

    Composite keywords:
    10  nucleus: stability [36, 14]
    6  saturation: density [25, 31]
    6  energy: symmetry [35, 11]
    4  nucleon: density [13, 31]
    3  energy: Coulomb [35, 3]
    2  energy: density [35, 31]
    2  nuclear matter: asymmetry [21, 2]
    1  n: matter [54, 36]
    1  n: density [54, 31]
    1  n: mass [54, 16]

    Single keywords:
    61  K0
    23  equation of state
    12  slope
    4  mass number
    4  nuclide
    3  nuclear model
    3  mass formula
    2  charge distribution
    2  elastic scattering
    2  binding energy


Thesaurus
=========

Classifier performs an extraction of keywords based on the recurrence
of specific terms, taken from a controlled vocabulary. A controlled
vocabulary is a thesaurus of all the terms that are relevant in a
specific context. When a context is defined by a discipline or branch of
knowledge then the vocabulary is said to be a *subject thesaurus*.
Various existing subject thesauri can be found
`here <http://www.fbi.fh-koeln.de/institut/labor/Bir/thesauri_new/thesen.htm>`__.

A subject thesaurus can be expressed in several different formats.
Different institutions/disciplines have developed different ways of
representing their vocabulary systems. The taxonomy used by classifier
is expressed in RDF/SKOS. It allows not only to list keywords but to
specify relations between the keywords and alternative ways to represent
the same keyword.

.. code-block:: xml

        <Concept rdf:about="http://cern.ch/thesauri/HEP.rdf#scalar">
         <composite rdf:resource="http://cern.ch/thesauri/HEP.rdf#Composite.fieldtheoryscalar"/>
         <prefLabel xml:lang="en">scalar</prefLabel>
         <note xml:lang="en">nostandalone</note>
        </Concept>

        <Concept rdf:about="http://cern.ch/thesauri/HEP.rdf#fieldtheory">
         <composite rdf:resource="http://cern.ch/thesauri/HEP.rdf#Composite.fieldtheoryscalar"/>
         <prefLabel xml:lang="en">field theory</prefLabel>
         <altLabel xml:lang="en">QFT</altLabel>
         <hiddenLabel xml:lang="en">/field theor\w*/</hiddenLabel>
         <note xml:lang="en">nostandalone</note>
        </Concept>

        <Concept rdf:about="http://cern.ch/thesauri/HEP.rdf#Composite.fieldtheoryscalar">
         <compositeOf rdf:resource="http://cern.ch/thesauri/HEP.rdf#scalar"/>
         <compositeOf rdf:resource="http://cern.ch/thesauri/HEP.rdf#fieldtheory"/>
         <prefLabel xml:lang="en">field theory: scalar</prefLabel>
         <altLabel xml:lang="en">scalar field</altLabel>
        </Concept>


In RDF/SKOS, every keyword is wrapped around a *concept* which
encapsulates the full semantics and hierarchical status of a term -
including synonyms, alternative forms, broader concepts, notes and so on
- rather than just a plain keyword.

The specification of the SKOS language and `various
manuals <http://www.w3.org/TR/2005/WD-swbp-thesaurus-pubguide-20050517/>`__
that aid the building of a semantic thesaurus can be found at the `SKOS
W3C
website <http://www.w3.org/TR/2005/WD-swbp-skos-core-guide-20051102/>`__.
Furthermore, Classifier can function on top of an extended version of
SKOS, which includes special elements such as key chains, composite
keywords and special annotations.

Keyword extraction
==================

Classifier computes the keywords of a fulltext document based on the
frequency of thesaurus terms in it. In other words, it calculates how
many times a thesaurus keyword (and its alternative and hidden labels,
defined in the taxonomy) appears in a text and it ranks the results.
Unlike other similar systems, Classifier does not use any machine
learning or AI methodologies - a just plain phrase matching using
`regular expressions <http://en.wikipedia.org/wiki/Regex>`__: it
exploits the conformation and richness of the thesaurus to produce
accurate results. It is then clear that Classifier performs best on top
of rich, well-structured, subject thesauri expressed in the RDF/SKOS
language.

Happy hacking and thanks for flying Invenio-Classifier.

| Inspirehep Development Team
|   Email: admin@inspirehep.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware-contrib/invenio-classifier
|   URL: http://inveniosoftware.org
