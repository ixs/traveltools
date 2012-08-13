#!/usr/bin/python

import pprint
import urllib
import urllib2
import simplejson as json
import xml.sax.saxutils
import subprocess
import sys

# The Carlson PDF
f = 'Carlson-LocationsDirectory.pdf'

# The address translation mapping to make geocoding work
addressMap = json.load(open('carlson-address-mapping.json'))

# The address translation mapping to make geocoding work
addressCache = json.load(open('carlson-address-cache.json'))

def pdfToText(file):
    print 'Converting %s to .txt' % (file)
    # We're forking out to pdftotext as pypdf cannot parse the file
    subprocess.call(['pdftotext', file])
    return file.replace('.pdf', '.txt')
    

def geocode(address):
    # Override addresses if needed
    try:
        address = addressMap[address]
    except KeyError:
        pass

    # Check if we have the geocoding data already cached
    try:
        return addressCache[unicode(address, 'iso-8859-1')]['results'][0]['geometry']['location']
    except KeyError:
        print 'Cache Miss for %s' % (address)
        url = 'http://maps.googleapis.com/maps/api/geocode/json?%s' % (urllib.urlencode({'address': address, 'sensor': 'false'}))
        ret = urllib2.urlopen(url).read()
        j = json.loads(ret)
        addressCache[unicode(address, 'iso-8859-1')] = j

	# Write out address cache
	# More IO but we do save on network lookups
#	json.dump(addressCache, open('carlson-address-cache.json', 'w'), indent=" ")
	json.dump(addressCache, open('carlson-address-cache.json', 'w'))

        try:
            return j['results'][0]['geometry']['location']
        except IndexError:
            return {'lng': '0.000000', 'lat': '0.000000'}
    except IndexError:
        return {'lng': '0.000000', 'lat': '0.000000'}


def formatKml(blocks):
    s = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
    s += '<kml xmlns="http://www.opengis.net/kml/2.2">' + "\n"
    s += '<Document>' + "\n"
    s += '  <name>Rezidor Hotels Worldwide</name>' + "\n"

    for color in ['blue', 'red', 'green', 'yellow', 'lightblue', 'purple', 'pink', 'orange']:
        s += '''  <Style id="%s">
    <IconStyle>
      <Icon>
        <href>http://maps.gstatic.com/mapfiles/ms2/micons/%s.png</href>
      </Icon>
    </IconStyle>
  </Style>''' % (color, color)

    for b in blocks:
        if len(b) <= 3:
            continue
#        if 'Germany' in b[1]:
        if True: # NOOP
            name = xml.sax.saxutils.escape(b[0])
            address = b[1]
            address = address.replace('\xc2\xa0\xc2\xb7\xc2\xa0', ' - ')
            geo = geocode(address)
            address = xml.sax.saxutils.escape(address)
            if 'Park Inn' in name:
                style = 'red'
            elif 'Radisson' in name:
                style = 'blue'
            elif 'Park Plaza' in name:
                style = 'lightblue'
            elif 'by park plaza' in name:
                style = 'orange'
            elif 'Country Inn' in name:
                style = 'green'
            else:
                style = 'yellow'

            s += '  <Placemark>' + "\n"
            s += '    <name>%s</name>' % (name)  + "\n"
            s += '    <address>%s</address>' % (address) + "\n"
#            print '    <Location>'
#            print '      <latitude>%s</latitude>' % (geo['lat'])
#            print '      <longitude>%s</longitude>' % (geo['lng'])
#            print '    </Location>'
            s += '    <styleUrl>#%s</styleUrl>' % (style)  + "\n"
            s += '    <Point>' + "\n"
            s += '      <coordinates>%s,%s</coordinates>' % (geo['lng'], geo['lat'])  + "\n"
            s += '    </Point>' + "\n"
            s += '  </Placemark>' + "\n"
        else:
            continue

    s += '</Document>' + "\n"
    s += '</kml>' + "\n"
    return s

# Collect blocks, then see what to do
file = pdfToText(f)
blocks = list()
block = list()
for line in open(file):
    if line.strip() == 'Radisson toll-free numbers':
        break
    if len(line) > 1:
        block.append(line.strip())
    else:
        blocks.append(block)
        block = list()

# Print KML
kml = formatKml(blocks)
fd = open(f.replace('.pdf', '.kml'), 'w')
fd.write(kml)
