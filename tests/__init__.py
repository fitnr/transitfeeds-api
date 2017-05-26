#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
import sys
from os import path
import json
from datetime import date, datetime
from unittest import TestCase
from transitfeeds import api
from transitfeeds import models

if (sys.version_info >= (3, 0)):
    unicode = str

class TransitFeedsTest(TestCase):

    def setUp(self):
        self.tf = api.TransitFeeds('nope')

    def test_FeedVersion(self):
        with open(path.join(path.dirname(__file__), 'data/getFeedVersions.json')) as f:
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
        with open(path.join(path.dirname(__file__), 'data/getFeeds.json')) as f:
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
