#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
from __future__ import print_function
import sys
import os
import csv
from datetime import datetime
from argparse import ArgumentParser
from transitfeeds import TransitFeeds

FEED_HELP = 'Fetch the versions of a feed in the Transitfeeds database'
LOCATION_HELP = "Fetch locations in the Transitfeeds database"


def parse_date(datestr):
    try:
        return datetime.strptime(datestr, '%Y-%m-%d').date()
    except ValueError:
        print('invalid date', datestr, file=sys.stderr)
        sys.exit(1)


def location_cli(api, **kwargs):
    if kwargs['list']:
        locations = api.locations()
        rows = [[loc.id, loc.title.encode('utf8'), loc.name.encode('utf8'), loc.coords[0], loc.coords[1]] for loc in locations]
        if kwargs.get('header'):
            rows.insert(0, ['id', 'title', 'name', 'longitude', 'latitude'])

    elif kwargs['id'] is None:
        print('A location-id required', file=sys.stderr)
        sys.exit(1)

    else:
        # get feed objects for the location
        feeds = api.feeds(location=kwargs['id'])
        rows = [[feed.id, feed.title.encode('utf8')] for feed in feeds]

    return rows


def feed_cli(api, **kwargs):
    if kwargs['id'] is None:
        print('A feed-id required', file=sys.stderr)
        sys.exit(1)

    start = parse_date(kwargs['start']) if kwargs.get('start') else None
    finish = parse_date(kwargs['finish']) if kwargs.get('finish') else None

    # Fetch all the feeds for this ID
    feedversions = api.feed_versions(kwargs.get('id'))

    # Filter by date
    rows = []
    if kwargs.get('header'):
        if kwargs.get('bare'):
            rows.append(['url'])
        else:
            rows.append(['feed id', 'published', 'start date', 'end date', 'url'])

    for fv in feedversions:
        if finish and fv.dates['start'] > finish:
            continue

        if start and fv.dates['finish'] < start:
            continue

        if kwargs.get('bare'):
            rows.append([fv.url.encode('utf8')])
        else:
            try:
                feed_start = fv.dates['start'].strftime('%Y-%m-%d')
            except (KeyError, AttributeError):
                feed_start = ''

            try:
                feed_finish = fv.dates['finish'].strftime('%Y-%m-%d')
            except (KeyError, AttributeError):
                feed_finish = ''

            rows.append([fv.id, fv.timestamp.strftime('%Y-%m-%d'), feed_start, feed_finish, fv.url])

    return rows


def add_boilerplate(parser):
    parser.add_argument('--key', default=os.environ.get('TRANSITFEEDS_API_KEY'),
                        help=("Transitfeeds API key. Can be passed as an argument or "
                              "read from the TRANSITFEEDS_API_KEY environment variable"))
    parser.add_argument('id', type=str, nargs='?', default=None)
    parser.add_argument('-H', '--header', action='store_true', help='Add a header to the output')


def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()

    location = subparsers.add_parser("location", help=LOCATION_HELP, description=LOCATION_HELP)
    add_boilerplate(location)
    location.add_argument('--list', action='store_true')
    location.set_defaults(func=location_cli)

    feed = subparsers.add_parser("feed", description=FEED_HELP, help=FEED_HELP,
                                 epilog=('By default the following columns are included: '
                                         'feed version id, date published, feed start date, feed end date, feed URL')
                                 )
    add_boilerplate(feed)
    feed.add_argument('--start', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--finish', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--bare', action='store_true', help='Return only the feed URL, omitting feed metadata')
    feed.set_defaults(func=feed_cli)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    api = TransitFeeds(args.key)

    rows = args.func(api, **vars(args))

    writer = csv.writer(sys.stdout, delimiter='\t')
    for row in rows:
        writer.writerow(row)

if __name__ == '__main__':
    main()
