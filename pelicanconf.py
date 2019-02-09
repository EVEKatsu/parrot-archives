#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Parrot'
SITENAME = 'Parrot Archives'
SITEURL = 'http://localhost:8000'

PATH = 'content'

TIMEZONE = 'Asia/Tokyo'

DEFAULT_LANG = 'ja'
#DEFAULT_DATE_FORMAT = '%d, %-m %Y'
THEME = 'theme'

FAVICON = 'favicon.jpg'
FAVICON_TYPE = 'image/jpg'

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/' + FAVICON: {'path': FAVICON},
    'extra/logo.jpg': {'path': 'logo.jpg'},
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10


TAGS_URL           = 'tags'
TAGS_SAVE_AS       = 'tags/index.html'
ARCHIVES_URL       = 'archives'
ARCHIVES_SAVE_AS   = 'archives/index.html'
ABOUT_URL          = 'about'
ABOUT_URL_SAVE_AS  = 'about.html'

MENU_INTERNAL_PAGES = (
    ('Tags', TAGS_URL, TAGS_SAVE_AS),
    ('Archives', ARCHIVES_URL, ARCHIVES_SAVE_AS),
    ('About', ABOUT_URL, ABOUT_URL_SAVE_AS),
)
# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True