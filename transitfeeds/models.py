#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
from datetime import datetime

URL_KEY_MAP = {'i': 'info', 'd': 'download'}
DATE_KEY_MAP = {'s': 'start', 'f': 'finish'}


def ymd_to_date(ymd):
    fmt = '%Y%m%d'
    return datetime.strptime(ymd, fmt).date()


class TransitObject(object):

    def __init__(self, kwargs):
        self.__dict__ = kwargs

    @property
    def id(self):
        return self.__dict__.get('id')

    @property
    def json(self):
        return self.__dict__


class Location(TransitObject):

    """Represents a single GTFS-covered place"""

    def __init__(self, **kwargs):
        super(Location, self).__init__(kwargs)

    @property
    def parent_id(self):
        return self.__dict__.get('pid')

    @property
    def title(self):
        return self.__dict__.get('t')

    @property
    def name(self):
        return self.__dict__.get('n')

    @property
    def coords(self):
        '''Returns lon, lat coordinates'''
        return self.__dict__.get('lng'), self.__dict__.get('lat')


class Feed(TransitObject):
    '''Metadata about a single GTFS feed'''

    _location = None
    _url = {}
    _timestamp = None

    def __init__(self, **kwargs):
        super(Feed, self).__init__(kwargs)

    @property
    def id(self):
        return self.__dict__.get('id')

    @property
    def type(self):
        return self.__dict__.get('ty')

    @property
    def title(self):
        return self.__dict__.get('t')

    @property
    def location(self):
        if self._location is None and 'l' in self.__dict__:
            self._location = Location(**self.__dict__['l'])

        return self._location

    @property
    def url(self):
        if len(self._url) == 0 and 'u' in self.__dict__:
            try:
                self._url = {URL_KEY_MAP.get(k, k): v for k, v in self.__dict__['u'].items()}
            except AttributeError:
                pass

        return self._url

    @property
    def latest(self):
        if self._timestamp is None and 'latest' in self.__dict__:
            ts = float(self.__dict__['latest'].get('ts', 0))
            self._timestamp = datetime.fromtimestamp(ts)
        return self._timestamp


class FeedVersionIssue(TransitObject):

    def __init__(self, **kwargs):
        super(FeedVersionIssue, self).__init__(kwargs)

    @property
    def filename(self):
        return self.__dict__.get('f')

    @property
    def line(self):
        return self.__dict__.get('l')

    @property
    def column(self):
        return self.__dict__.get('c')

    @property
    def message(self):
        return self.__dict__.get('m')


class FeedVersion(TransitObject):
    '''Represents a past version of a GTFS dataset'''

    _feed = None
    _timestamp = None
    _err = []
    _warn = []
    _dates = {}

    def __init__(self, **kwargs):
        super(FeedVersion, self).__init__(kwargs)

    @property
    def feed(self):
        if self._feed is None and 'f' in self.__dict__:
            self._feed = Feed(**self.__dict__['f'])

        return self._feed

    @property
    def timestamp(self):
        if self._timestamp is None and 'ts' in self.__dict__:
            self._timestamp = datetime.fromtimestamp(float(self.__dict__['ts']))

        return self._timestamp

    @property
    def size(self):
        return int(self.__dict__.get('size', 0))

    @property
    def url(self):
        return self.__dict__.get('url')

    @property
    def dates(self):
        if len(self._dates) == 0 and 'd' in self.__dict__:
            try:
                self._dates = {DATE_KEY_MAP.get(k, k): ymd_to_date(v)
                               for k, v in self.__dict__['d'].items()}
            except AttributeError:
                pass

        return self._dates

    @property
    def err(self):
        if len(self._err) == 0 and 'err' in self.__dict__:
            self._err = [FeedVersionIssue(**x) for x in self.__dict__['err']]

        return self._err

    @property
    def warn(self):
        if len(self._warn) == 0 and 'warn' in self.__dict__:
            self._warn = [FeedVersionIssue(**x) for x in self.__dict__['warn']]

        return self._warn
