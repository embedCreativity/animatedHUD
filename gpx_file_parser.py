import gpxpy
from pandas import DataFrame

# NOTES:  gpxpy doesn't use the speed extension value and the calculation below fucks it hard and creates a smattering of NaN values in
# the output.  Also, it would be really cool to grab the 'temp' temperature data from the gpx file as well.
# The extension name for speed is: <gpxdata:speed> - temperature is <gpxdata:temp>. Altitude data looks legit on initial inspection as
# the primary source is probably not taken from the extension information but the <ele> tag instead - although there is a copy of it in
# the extension information under the <gpxdata:altitude> tag. I guess it would also be neat to take the total traveled distance tag in
# extensions as well, although that is less awesome. It starts after the initial trkpt (starting at the second entry) and is labeled
# with the <gpxdata:distance> tag.
#
# Example: try this: 'segment.points[some index].extensions'  <-- You'll see XML garbage in there with all the extension field names
# we want, but how do we extract their values? They come out as an array of these garbage entries:
# <Element '{http://www.cluetrust.com/XML/GPXDATA/1/0}speed' at 0x7f5512f9cc28>
#
#### Example Usage ####
# >>> from gpx_file_parser import load_data
# >>> data = load_data('test.gpx')
# >>> data[0]
#     True
# >>> df = data[1]
#
# >>> df['Speed'].max()
#     16.2272790860947
# >>> df['Speed'].min()
#     0.0
# >>> df['Temperature'].min()
#     0.0
# >>> df['Temperature'].max()
#     29.399999618530298
# >>> df['Distance'].max()
#     50339.0
# >>> df['Distance'].min()
#     0.0
#

def load_data(filename):
    data = []

    gpx = gpxpy.parse(open(filename))
    # Error check input file for general sanity

    if 1 != len(gpx.tracks):
        print('ERROR: expecting a single track from gpx file')
        return (False, NULL)
    if 1 != len(gpx.tracks[0].segments):
        print('ERROR: expecting a single segment from gpx file')
        return (False, NULL)

    segment = gpx.tracks[0].segments[0]
    if 0 >= len(segment.points):
        print('ERROR: gpx file has {} points in file'.format(segment.points))
        return (False, NULL)

    # Loop through segments
    for point_idx, point in enumerate(segment.points):
        # Parse extensions data for our special data points
        altitude = point.elevation * 3.281 # convert from meters to feet
        speed = 0.0
        temperature = 0.0
        distance = 0.0
        for element in point.extensions:
            if -1 != element.tag.find('speed'):
                speed = float(element.text)
                # convert meters/second to MPH
                speed = speed * 2.237
            elif -1 != element.tag.find('temp'):
                temperature = float(element.text)
                # convert C to F
                temperature = (temperature * 9.0/5.0) + 32.0
            elif -1 != element.tag.find('distance'):
                distance = float(element.text)
                # convert from meters to miles
                distance = distance / 1609.344

        data.append([point.longitude,
                     point.latitude,
                     altitude,
                     point.time,
                     speed,
                     temperature,
                     distance ])

    columns = ['Longitude', 'Latitude', 'Altitude', 'Time', 'Speed', 'Temperature', 'Distance']
    df = DataFrame(data, columns=columns)

    return (True, df)
