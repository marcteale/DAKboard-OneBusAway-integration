# DAKboard OneBusAway integration

A Python script to display real time transit info from the OneBusAway API.  It can be integrated into a DAKboard custom screen layout in an external data (fetch) block.  DAKboard content is generated on their servers, so the output of busstop.py needs to be hosted on a publicly available web server.

The script requires that you have a OneBusAway API key, which you can request by emailing OBA_API_KEY@soundtransit.org.

# Usage

`$ ./busstop.py`

# Configuration

All configuration is pulled from busstop.conf.  You can get stop IDs by 
searching for your stop on https://onebusaway.org/.  Find your stop on the map,
select it, and click on "Complete timetable."  The ID will be the end of the
resulting URL.

e.g. URL=http://pugetsound.onebusaway.org/where/standard/schedule.action?id=1_575

ID=1_575

## Sample configuration:

    # Required sections
    [global]
    apikey = XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    server = http://api.pugetsound.onebusaway.org/
    jsonfile = youroutputfile.json

    [defaults]
    # Vehicles that have departed in the previous n minutes
    minutesbefore = 0
    # Vehicles departing in the next n minutes
    minutesafter = 30
    # Comma separated list of routes to filter on.
    # Delete this line to display all routes.
    routes = C Line, 8, 13

    # Stops only need a header with their stop ID to be shown.
    # 3rd and Pike NW bound, using all defaults:
    [1_575]

    # Defaults can be overridden if desired.
    # 3rd and Pike SE bound, overriding some defaults:
    [1_433]
    minutesbefore = 5
    routes = 19, 24,36

# Sample Output

    [
      {
        "subtitle": "predicted at 3:34 pm",
        "value": "124 - 0 minutes",
        "title": "3rd Ave & Pike St"
      },
      {
        "subtitle": "predicted at 3:34 pm",
        "value": "120 - 1 minute",
        "title": "3rd Ave & Pike St"
      },
      {
        "subtitle": "predicted at 3:35 pm",
        "value": "355E - 1 minute",
        "title": "3rd Ave & Pike St"
      },
      {
        "subtitle": "predicted at 3:33 pm",
        "value": "2 - 0 minutes",
        "title": "3rd Ave & Pike St"
      }
    ]

# References
- [OneBusAway API Reference](http://developer.onebusaway.org/modules/onebusaway-application-modules/1.1.13/api/where/index.html)
- [DAKboard External Data / Fetch Support Article](https://dakboard.freshdesk.com/support/solutions/articles/35000062047-external-data-fetch-formatting-options)
