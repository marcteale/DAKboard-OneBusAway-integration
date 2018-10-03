#!/usr/bin/env python3.6
import configparser
import json
import os
import sys
from datetime import datetime

import requests


def get_departures_for_stop(departures, stop_id, routes, minutes_before, minutes_after, server, apikey):
    """Fetch the departures for the requested stop and return them as a dict."""

    r = requests.get('{}/api/where/arrivals-and-departures-for-stop/{}.json'.format(server, stop_id),
                     params={'key': apikey, 'minutesBefore': minutes_before, 'minutesAfter': minutes_after})
    rj = r.json()
    stop_name = ''

    if r.ok:
        for stop in rj['data']['references']['stops']:
            if stop['id'] == stop_id:
                stop_name = stop['name']
                break

        current_time = datetime.fromtimestamp(rj['currentTime'] / 1000)
        if rj['data']['entry']['arrivalsAndDepartures']:
            for a in rj['data']['entry']['arrivalsAndDepartures']:
                if a['departureEnabled'] and (routes is None or a['routeShortName'] in routes):
                    if a['predicted'] and a['predictedDepartureTime'] != 0:
                        departure_string = 'predictedDepartureTime'
                    else:
                        departure_string = 'scheduledDepartureTime'
                    departure_time = datetime.fromtimestamp(a[departure_string] / 1000)
                    delta = int((departure_time - current_time).seconds / 60)
                    value = "{} - {} minute{}".format(a['routeShortName'], delta, '' if abs(delta) == 1 else 's')
                    subtitle = '{} at {}'.format(
                            departure_string.replace('DepartureTime', ''),
                            departure_time.strftime("%-I:%M %P"))
                    departures.append({'value': value, 'title': stop_name, 'subtitle': subtitle})

        else:
            departures.append(
                {'value': 'No scheduled departures', 'title': stop_name,
                 'subtitle': 'No departures schedule or predicted in the next {} minutes.'.format(minutes_after)}
            )
    else:
        departures.append({'value': 'Failed to fetch data', 'title': '', 'subtitle': rj['text']})
    return departures


def get_config():
    """Read the config file."""
    config = configparser.ConfigParser(allow_no_value=True)
    configfile = os.path.abspath(os.path.dirname(__file__)) + '/busstop.conf'
    config.read(configfile)

    routes = [unicode(r.strip()) for r in config.get('defaults', 'routes').split(',')] \
        if config.has_option('defaults', 'routes') else None
    defaults = {'minutesbefore': config.get('defaults', 'minutesbefore'),
                'minutesafter': config.get('defaults', 'minutesafter'),
                'routes': routes,
                'apikey': os.environ['APIKEY'],
                'server': config.get('defaults', 'server')}
    config.remove_section('defaults')
    config.remove_section('defaults')
    return config, defaults


def app(environ, start_response):
    status = "200 OK"
    try:
        config, defaults = get_config()
        results = []
        ok = True
    except Exception as e:
        status = "500 Internal Server Error"
        results = json.dumps({'title': 'Error', 'value': e.message, 'subtitle': ''})
        ok = False

    if ok:
        for section in config.sections():
            minsBefore = config.get(section, 'minutesbefore') \
                if config.has_option(section, 'minutesbefore') else defaults['minutesbefore']
            minsAfter = config.get(section, 'minutesafter') \
                if config.has_option(section, 'minutesafter') else defaults['minutesafter']
            routes = [unicode(r.strip()) for r in config.get(section, 'routes').split(',')] \
                if config.has_option(section, 'routes') else defaults['routes']
            stopId = section
            results = get_departures_for_stop(results, stopId, routes, minsBefore, minsAfter, defaults['server'],
                                              defaults['apikey'])

    data = str.encode(json.dumps(results))
    response_headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
