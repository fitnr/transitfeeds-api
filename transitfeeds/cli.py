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
from requests import Session
from transitfeeds import TransitFeeds


FEED_HELP = 'Fetch the versions of a feed on the Transitfeeds.com'
LOCATION_HELP = "Fetch feeds attached to locations on the Transitfeeds.com"

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
        raise ValueError(datestr)


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

    else:
        rows = [('feed-id', 'title')] if kwargs.get('header') else []
        # get feed objects for each location
        for i in ids:
            rows.extend([(f.id, utf8(f.title)) for f in api.feeds(location=i)])

    return rows


def feed_cli(api, **kwargs):
    ids = kwargs.get('ids', [])

    if kwargs.get('latest'):
        # Complicated list comprehension to filter out empty results.
        return [[x] for x in (api.latest(i) for i in ids) if x]

    try:
        start = strpdate(kwargs['start']) if kwargs.get('start') else None
        finish = strpdate(kwargs['finish']) if kwargs.get('finish') else None
    except ValueError as err:
        print('Invalid date:', err, file=sys.stderr)
        sys.exit(1)

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


def add_boilerplate(parser, kind, noun):
    parser.add_argument('--key', default=os.environ.get('TRANSITFEEDS_API_KEY'),
                        help=("Transitfeeds API key. Can be passed as an argument or "
                              "read from the TRANSITFEEDS_API_KEY environment variable"))
    parser.add_argument('ids', type=str, nargs='*', default=None, help='One or more {}-ids'.format(kind))
    parser.add_argument('-H', '--header', action='store_true', help='Add a header to the output')
    parser.add_argument('--bare', action='store_true', help='Return only the {0} {1}, omitting {0} metadata'.format(kind, noun))


def parse_args(input_args):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    location = subparsers.add_parser("location", help=LOCATION_HELP, description=LOCATION_HELP)
    add_boilerplate(location, 'location', 'id')
    location.add_argument('--list', action='store_true', help='Return a list of all locations')
    location.set_defaults(func=location_cli)

    feed = subparsers.add_parser("feed", description=FEED_HELP, help=FEED_HELP,
                                 epilog=('By default the following columns are included: '
                                         'feed-id-version, date published, feed start date, feed end date, feed URL')
                                 )
    add_boilerplate(feed, 'feed', 'url')
    feed.add_argument('--start', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--finish', type=str, help='yyyy-mm-dd format')
    feed.add_argument('--latest', action='store_true', help='Return only the URL of the newest feed')
    feed.set_defaults(func=feed_cli)

    if len(input_args) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(input_args)

    if getattr(args, 'list', False) is False and len(args.ids) == 0:
        p = feed if (args.func == feed_cli) else location
        p.print_help()
        sys.exit(1)

    with Session() as s:
        api = TransitFeeds(args.key, s)
        return args.func(api, **vars(args))

def main():
    rows = parse_args(sys.argv[1:])
    writer = csv.writer(sys.stdout, delimiter='\t')

    try:
        writer.writerows(rows)
    except (BrokenPipeError, IOError):
        sys.stderr.close()


if __name__ == '__main__':
    main()
