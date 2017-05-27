#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
import requests
from .models import Feed, FeedVersion, Location

statuses = {
    'OK': 'Request was valid.',
    'EMPTYKEY': 'Request was missing API key.',
    'MISSINGINPUT': 'A required request parameter was missing.',
    'INVALIDINPUT': 'A request parameter was invalid.',
}

METADATA_KEYS = {
    'total': 'total',
    'limit': 'limit',
    'page': 'page',
    'pages': 'numPages',
}


class TransitFeeds(object):

    base = 'https://api.transitfeeds.com/v1/'
    headers = {'Accept': 'application/json'}

    total = None
    limit = None
    page = None
    num_pages = None

    def __init__(self, key):
        self.key = key

    def locations(self):
        results = self._request_results('getLocations')
        return [Location(**x) for x in results['locations']]

    def feeds(self, location=None, descendants=None, **kwargs):
        '''
        Args:
            location (int): This is the unique ID of a location. If specified, feeds will only be returned that belong
                            to this location (and perhaps sub-locations too, depending on the descendants value). You
                            can use the /getLocations API endpoint to determine location IDs.
            descendants (bool): If a location is specified in location, this flag can be used to control if returned
                                feeds must be assigned directly to the location, or if feeds belonging to sub-locations
                                can also be returned. If 0, then feeds must be assigned directly to the specified
                                location.
            page (int): The page number of results to return. For example, if you specify a page of 2 with a limit of
                        10, then results 11-20 are returned. The number of pages available is included in the response.
            limit (int): The maximum number of results to return.
            type (str): ["gtfs" or "gtfsrealtime"] The type of feeds to return. If unspecified, feeds of all
                        types are returned.

        '''
        descendants = 1 if descendants else 0
        results = self._request_results('getFeeds', location=location, descendants=descendants, **kwargs)
        return [Feed(**f) for f in results['feeds']]

    def latest(self, feed):
        '''
            Args:
                feed (str): The ID of the feed to retrieve the latest feed version for.
                    Use `TransitFeeds.feeds` to discover feed IDs.
            Returns:
                (str) The URL of the latest feed
        '''
        r = self._request('getLatestFeedVersion', feed=feed, rargs={'allow_redirects': False})
        return r.headers.get('Location')

    def feed_versions(self, feed, err=None, warn=None, **kwargs):
        warn = warn or 1
        err = err or 1
        results = self._request_results('getFeedVersions', feed=feed, warn=warn, err=err, **kwargs)
        return [FeedVersion(**x) for x in results['versions']]

    def _request(self, operation, rargs=None, **params):
        params['key'] = self.key
        rargs = rargs or {}
        r = requests.get(self.base + operation, headers=self.headers, params=params, **rargs)
        return r

    def _request_results(self, operation, **params):
        r = self._request(operation, **params)
        result = r.json()

        if result['status'] != 'OK':
            raise RuntimeError('Transitfeeds: Attempted to fetch {}, got back status: {} ({})'.format(
                operation, result['status'], statuses[result['status']])
            )

        # try to set metadata about query
        for key in METADATA_KEYS.keys():
            setattr(self, key, result['results'].get(METADATA_KEYS[key]))

        return result['results']
