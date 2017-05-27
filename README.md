transitfeeds-api
================

Work with the [Transitfeeds](http://transitfeeds.com) API. Not affiliated with Transitfeeds.

## Command line tool

The command line tool returns feeds as tab-separated data. An [API key](http://transitfeeds.com/api/keys) is required. It can be specified with either the `--key` option or the `TRANSITFEEDS_API_KEY` environment variable.

Fetch a list of locations:
````
transitfeeds location --list --header
````
````
location-id	title	name	longitude	latitude
606	Aachen, Germany	Aachen	6.083887	50.775346
416	Addison County, VT, USA	Addison County	-73.164338	44.119729
4	Adelaide SA, Australia	Adelaide	138.599959	-34.928621
99	Africa	Africa	34.508523	-8.783195
11	Airlie Beach QLD 4802, Australia	Airlie Beach	148.718456	-20.26872
237	Alabama, USA	Alabama	-86.902298	32.318231
276	Alaska, USA	Alaska	-149.493673	64.200841
328	Albany, OR, USA	Albany	-123.105928	44.636511
````

Fetch the feeds associated with one or more given locations:
````
transitfeeds location 606 416 4 99
````
````
aachener-verkehrsverbund/836	AAV GTFS
addison-county-transit/556	ACTR GTFS
adelaide-metro/1	Adelaide Metro GTFS
adelaide-metro/72	Adelaide Metro Developer Group
adelaide-metro/77	Adelaide Metro Twitter
````

Fetch the versions of one or more feeds:
````
transitfeeds feed mta/87 mta/81 --header
````
````
feed-id	published	start-date	end-date	url
mta/87/20170522	2017-05-23	2017-05-22	2017-10-07	https://transitfeeds.com/p/mta/87/20170522/download
mta/87/20170331	2017-03-31	2017-03-31	2017-09-30	https://transitfeeds.com/p/mta/87/20170331/download
mta/87/20170330	2017-03-30	2017-03-30	2017-09-30	https://transitfeeds.com/p/mta/87/20170330/download
...
mta/81/20151223	2015-12-23	2016-01-03	2016-04-02	https://transitfeeds.com/p/mta/81/20151223/download
mta/81/20151124	2015-11-24	2015-09-06	2016-01-02	https://transitfeeds.com/p/mta/81/20151124/download
mta/81/20150921	2015-09-22	2015-09-06	2016-01-02	https://transitfeeds.com/p/mta/81/20150921/download
````

Fetch feed editions between given dates for one or more feeds:
````
transitfeeds feed mta/87 --start 2016-12-01 --finish 2017-01-01 --header
````
````
feed-id	published	start-date	end-date	url
mta/87/20161210	2016-12-10	2016-12-09	2017-04-01	https://transitfeeds.com/p/mta/87/20161210/download
mta/87/20161208	2016-12-08	2016-12-07	2017-04-01	https://transitfeeds.com/p/mta/87/20161208/download
mta/87/20161122	2016-11-22	2016-11-21	2017-04-01	https://transitfeeds.com/p/mta/87/20161122/download
mta/87/20161012	2016-10-12	2016-10-12	2017-04-01	https://transitfeeds.com/p/mta/87/20161012/download
mta/87/20160928	2016-09-28	2016-09-27	2017-04-01	https://transitfeeds.com/p/mta/87/20160928/download
````

(Note that this includes any editions of a feed that overlap the interval.)

Fetch the most recent version of one or more feeds:
````
transitfeeds feed mta/87 --latest
````
````
https://transitfeeds-data.s3-us-west-1.amazonaws.com/public/feeds/mta/87/20170522/gtfs.zip
````
This returns only the URL.


## Python API

Example:
````python
from transitfeeds import TransitFeeds

API_KEY = '<your api key here>'
tf = TransitFeeds(API_KEY)

feedid = 'mta/80'
versions = tf.feed_versions(feedid)

for v in versions:
	print(v.url)

for v in versions:
	print(v.dates['start'])
````
````
https://transitfeeds.com/p/mta/80/20170404/download
https://transitfeeds.com/p/mta/80/20170109/download
https://transitfeeds.com/p/mta/80/20151124/download
https://transitfeeds.com/p/mta/80/20150921/download
https://transitfeeds.com/p/mta/80/20150828/download
https://transitfeeds.com/p/mta/80/20150709/download
datetime.date(2017, 4, 8)
datetime.date(2017, 1, 7)
datetime.date(2015, 9, 5)
datetime.date(2015, 9, 5)
datetime.date(2015, 9, 5)
datetime.date(2015, 6, 27)
````