#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
from os import path
import json
from datetime import date, datetime
from unittest import TestCase
from transitfeeds import api
from transitfeeds import models


class TransitFeedsTest(TestCase):

    def setUp(self):
        self.tf = api.TransitFeeds('nope')

    def test_FeedVersion(self):
        with open(path.join(path.dirname(__file__), 'data/getFeedVersions.json')) as f:
            data = json.load(f)

        fvs = [models.FeedVersion(**x) for x in data['results']['versions']]

        assert len(fvs) > 0
        self.assertIsInstance(fvs[0], models.FeedVersion)

        assert hasattr(fvs[1], 'feed')
        self.assertIsInstance(fvs[1].size, int)
        self.assertIsInstance(fvs[1].timestamp, datetime)

        self.assertIsInstance(fvs[1].dates['start'], date)

        issue = fvs[0].err
        assert len(issue) > 0
        assert hasattr(issue[0], 'message')
        assert hasattr(issue[0], 'filename')
        assert hasattr(issue[0], 'line')

    def test_helpers(self):
        d = date(2016, 10, 1)
        assert d == models.ymd_to_date('2016101')
