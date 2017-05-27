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

if (sys.version_info >= (3, 0)):
    def utf8(text):
        return text

else:
    BrokenPipeError = IOError

    def utf8(text):
        return text.encode('utf8')


def strpdate(datestr):
    try:
        return datetime.strptime(datestr, '%Y-%m-%d').date()
    except ValueError:
        print('invalid date', datestr, file=sys.stderr)
        sys.exit(1)


def strfdate(date):
    try:
        return date.strftime('%Y-%m-%d')
    except AttributeError:
        return ''


def location_cli(api, **kwargs):
    ids = kwargs.get('ids', [])

    if kwargs['list']:
        locations = api.locations()
        rows = [('location-id', 'title', 'name', 'longitude', 'latitude')] if kwargs.get('header') else []
        rows.extend([(loc.id, utf8(loc.title), utf8(loc.name), loc.coords[0], loc.coords[1]) for loc in locations])

    elif len(ids) == 0:
        print('A location-id required', file=sys.stderr)
        sys.exit(1)

    else:
        rows = [('feed-id', 'title')] if kwargs.get('header') else []
        # get feed objects for each location
        for i in ids:
            rows.extend([(f.id, utf8(f.title)) for f in api.feeds(location=i)])

    return rows


def feed_cli(api, **kwargs):
    ids = kwargs.get('ids', [])

    if len(ids) == 0:
        print('A feed-id required', file=sys.stderr)
        sys.exit(1)

    if kwargs.get('latest'):
        # Complicated list comprehension to filter out empty results.
        return [[x] for x in (api.latest(i) for i in ids) if x]

    start = strpdate(kwargs['start']) if kwargs.get('start') else None
    finish = strpdate(kwargs['finish']) if kwargs.get('finish') else None

    # Filter by date
    rows = []
    if kwargs.get('header'):
        row = ('url',) if kwargs.get('bare') else ('feed-id', 'published', 'start-date', 'end-date', 'url')
        rows.append(row)

    for i in ids:
        # Fetch all the feeds for this ID
        feedversions = api.feed_versions(i)

        for fv in feedversions:
            if finish and fv.dates['start'] > finish:
                continue

            if start and fv.dates['finish'] < start:
                continue

            if kwargs.get('bare'):
                row = (utf8(fv.url),)
            else:
                f_start = strfdate(fv.dates.get('start', ''))
                f_finish = strfdate(fv.dates.get('finish', ''))
                row = (utf8(fv.id), fv.timestamp.strftime('%Y-%m-%d'), f_start, f_finish, fv.url)

            rows.append(row)

    return rows


def add_boilerplate(parser, kind):
    parser.add_argument('--key', default=os.environ.get('TRANSITFEEDS_API_KEY'),
                        help=("Transitfeeds API key. Can be passed as an argument or "
                              "read from the TRANSITFEEDS_API_KEY environment variable"))
    parser.add_argument('ids', type=str, nargs='*', default=None, help='One or more {}-ids'.format(kind))
    parser.add_argument('-H', '--header', action='store_true', help='Add a header to the output')


def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()

    location = subparsers.add_parser("location", help=LOCATION_HELP, description=LOCATION_HELP)
    add_boilerplate(location, 'location')
    location.add_argument('--list', action='store_true')
    location.set_defaults(func=location_cli)

    feed = subparsers.add_parser("feed", description=FEED_HELP, help=FEED_HELP,
                                 epilog=('By default the following columns are included: '
                                         'feed-id-version, date published, feed start date, feed end date, feed URL')
                                 )
    add_boilerplate(feed, 'feed')
    feed.add_argument('--start', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--finish', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--latest', action='store_true', help='Return only the URL of the newest feed')
    feed.add_argument('--bare', action='store_true', help='Return only the feed URL, omitting feed metadata')
    feed.set_defaults(func=feed_cli)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    api = TransitFeeds(args.key)

    rows = args.func(api, **vars(args))
    writer = csv.writer(sys.stdout, delimiter='\t')

    try:
        writer.writerows(rows)
    except (BrokenPipeError, IOError):
        sys.stderr.close()


if __name__ == '__main__':
    main()
