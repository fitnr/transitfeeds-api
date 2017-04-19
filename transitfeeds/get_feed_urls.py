#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
from __future__ import print_function
import sys
import csv
from datetime import datetime
from argparse import ArgumentParser
from transitfeeds import TransitFeeds


def main():
    parser = ArgumentParser()
    parser.add_argument('--key', required=True)
    parser.add_argument('--get-locations', action='store_true')
    parser.add_argument('--location-id', type=str)

    parser.add_argument('--feed-id', type=str)
    parser.add_argument('--start', type=str)
    parser.add_argument('--finish', type=str)

    parser.add_argument('--bare', action='store_true')

    args = parser.parse_args()

    if (args.get_locations is None and
            args.location_id is None and
            args.feed_id is None):
        print('Require ask for location or provide a feed id', file=sys.stderr)
        exit(1)

    api = TransitFeeds(args.key)

    if args.feed_id:
        rows = []

        if args.start or args.finish:
            if args.start:
                try:
                    args.start = datetime.strptime(args.start, '%Y-%m-%d').date()
                except ValueError:
                    print('invalid date', args.start, file=sys.stderr)
                    exit(1)

            if args.finish:
                try:
                    args.finish = datetime.strptime(args.finish, '%Y-%m-%d').date()
                except ValueError:
                    print('invalid date', args.finish, file=sys.stderr)
                    exit(1)

            feedversions = api.feed_versions(args.feed_id)

            for fv in feedversions:
                if args.finish and fv.dates['start'] > args.finish:
                    continue
                if args.start and fv.dates['finish'] < args.start:
                    continue

                if args.bare:
                    rows.append([fv.url.encode('utf8')])
                else:
                    rows.append([fv.id, fv.timestamp.strftime('%Y-%m-%d'), fv.url])

        else:
            rows = []
            print(api.latest(args.feed_id), file=sys.stderr)

    elif args.get_locations:
        locations = api.locations()
        rows = ([loc.id, loc.title.encode('utf8'), loc.name.encode('utf8')] for loc in locations)

    elif args.location_id:
        # get feed objects for the location
        feeds = api.feeds(location=args.location_id)
        rows = [[feed.id, feed.title.encode('utf8')] for feed in feeds]

    writer = csv.writer(sys.stdout, delimiter='\t')
    for row in rows:
        writer.writerow(row)

if __name__ == '__main__':
    main()
