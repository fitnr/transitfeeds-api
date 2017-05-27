#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
import sys
import os
from io import StringIO
import warnings
import json
from datetime import date, datetime
import unittest
from transitfeeds import api, cli, models

if (sys.version_info >= (3, 0)):
    unicode = str


class TransitFeedsTest(unittest.TestCase):

    def self_test_init(self):
        tf = api.TransitFeeds('nope')
        self.assertIsInstance(tf, api.TransitFeeds)

    def test_FeedVersion(self):
        with open(os.path.join(os.path.dirname(__file__), 'data/getFeedVersions.json')) as f:
            data = json.load(f)

        fvs = [models.FeedVersion(**x) for x in data['results']['versions']]

        assert len(fvs) > 0
        self.assertIsInstance(fvs[0], models.FeedVersion)

        for fv in fvs:
            assert hasattr(fv, 'feed')
            self.assertIsInstance(fv.size, int)
            self.assertIsInstance(fv.timestamp, datetime)
            self.assertIsInstance(fv.dates['start'], date)

        issue = fvs[0].err
        assert len(issue) > 0
        assert hasattr(issue[0], 'message')
        assert hasattr(issue[0], 'filename')
        assert hasattr(issue[0], 'line')

    def test_helpers(self):
        d = date(2016, 10, 1)
        self.assertEqual(d, models.ymd_to_date('2016101'))

    def test_feeds(self):
        with open(os.path.join(os.path.dirname(__file__), 'data/getFeeds.json')) as f:
            data = json.load(f)

        feeds = [models.Feed(**x) for x in data['results']['feeds']]
        for feed in feeds:
            self.assertIsInstance(feed.id, unicode)
            self.assertIsInstance(feed.title, unicode)
            self.assertIsInstance(feed.url, dict)
            self.assertEqual(feed.type, "gtfs")
            self.assertIsInstance(feed.latest, datetime)
            self.assertIsInstance(feed.location, models.Location)
            self.assertIsInstance(feed.location.parent_id, int)
            self.assertIsInstance(feed.location.title, unicode)
            self.assertIsInstance(feed.location.name, unicode)
            self.assertIsInstance(feed.location.coords, tuple)
            self.assertIsInstance(feed.location.coords[0], float)

    def test_cli_location(self):
        cmd = 'location -H 432'.split()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rows = cli.parse_args(cmd)
        self.assertSequenceEqual(('feed-id', 'title'), rows[0])

    def test_cli_feed(self):
        cmd = 'feed -H mta/80'.split()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rows = cli.parse_args(cmd)

        self.assertSequenceEqual(('feed-id', 'published', 'start-date', 'end-date', 'url'), rows[0])

    def test_dates(self):
        d = date(2017, 1, 1)
        s = '2017-01-01'
        self.assertEqual(s, cli.strfdate(d))
        self.assertEqual(d, cli.strpdate(s))
        self.assertEqual('', cli.strfdate(''))

    def test_cli_help(self):
        sys.stderr = sys.stdout = StringIO()

        with self.assertRaises(SystemExit):
            cli.parse_args([])

        with self.assertRaises(SystemExit):
            cli.parse_args(['feed'])

        with self.assertRaises(SystemExit):
            cli.parse_args('feed 1 --start foobar'.split())

        with self.assertRaises(SystemExit):
            cli.parse_args(['location'])

if __name__ == '__main__':
    unittest.main()
