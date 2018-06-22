#!/usr/bin/env python
import ConfigParser
import json
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
                    departure_string = 'predictedDepartureTime' if a['predicted'] else 'scheduledDepartureTime'
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


if __name__ == '__main__':
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read('busstop.conf')

    apikey = config.get('global', 'apikey')
    server = config.get('global', 'server')
    jsonfile = config.get('global', 'jsonfile')
    defaultMinsBefore = config.get('defaults', 'minutesbefore')
    defaultMinsAfter = config.get('defaults', 'minutesafter')
    config.remove_section('global')
    config.remove_section('defaults')
    results = []

    for section in config.sections():
        minsBefore = config.get(section, 'minutesbefore') \
            if config.has_option(section, 'minutesbefore') else defaultMinsBefore
        minsAfter = config.get(section, 'minutesafter') \
            if config.has_option(section, 'minutesafter') else defaultMinsAfter
        routes = [unicode(r.strip()) for r in config.get(section, 'routes').split(',')] \
            if config.has_option(section, 'routes') else None
        stopId = section
        results = get_departures_for_stop(results, stopId, routes, minsBefore, minsAfter, server, apikey)

    with open(jsonfile, 'w') as outfile:
        json.dump(results, outfile)
