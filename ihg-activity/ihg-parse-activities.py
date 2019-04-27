#!/usr/bin/python3
# -*- coding: UTF-8

import datetime
import json
import pprint
import sys
import tabulate

data = json.load(open(sys.argv[1]))

current_year_only = True
headers = ('Date', 'Description', 'Activity', 'EQP', 'Nights')
summary = []
sum = 0
nights = 0

def is_current(activity):
    if activity['activityDetails']['checkOutDate'] is not None:
      if datetime.datetime.strptime(activity['activityDetails']['checkOutDate'], '%Y-%m-%d %H:%M:%S.%f').year < datetime.date.today().year:
        return False
    else:
      if datetime.datetime.strptime(activity['activitySummary']['datePosted'], '%Y-%m-%d %H:%M:%S.%f').year < datetime.date.today().year:
        return False
    return True

for a in data['activities']:
    if current_year_only and not is_current(a):
        continue
    ad = []
    desc = []
    ad.append(a['activitySummary']['datePosted'].split()[0])
    desc.append(a['activitySummary']['description'])
    hotel_code = a['activityDetails']['hotelMnemonic']
    if hotel_code is not None:
        desc.append(data['hotel_details'][hotel_code]['hotelInfo']['brandInfo']['brandName'])
        desc.append(data['hotel_details'][hotel_code]['hotelInfo']['profile']['name'])
    ad.append('\n'.join(desc))
    ad.append(a['activitySummary']['totalEarnedValue'])
    points = a['activitySummary']['eliteQualifyingPointValue']
    sum += points/10
    ad.append(points)
    qn = a['activityDetails']['qualifyingNights']
    nights += qn
    ad.append(qn)
    summary.append(ad)

print(tabulate.tabulate(summary, headers=headers))
print("Total spend: USD {:.2f}".format(sum))
print("Total qualifying nights: {:d}".format(nights))


print()
print()
print('IC Stays')

headers = ('Date', 'Description', 'EQP', 'USD', 'Nights')
ic_stays = []
sum = 0
nights = 0

for a in data['activities']:
    if current_year_only and not is_current(a):
        continue
    hotel_code = a['activityDetails']['hotelMnemonic']
    if hotel_code is not None:
        brand = data['hotel_details'][hotel_code]['hotelInfo']['brandInfo']['brandCode']
    else:
        brand = None
    if brand == 'ICON':
        ad = []
        desc = []
        ad.append(a['activitySummary']['datePosted'].split()[0])
        desc.append(a['activitySummary']['description'])
        desc.append(data['hotel_details'][hotel_code]['hotelInfo']['brandInfo']['brandName'])
        desc.append(data['hotel_details'][hotel_code]['hotelInfo']['profile']['name'])
        ad.append('\n'.join(desc))
        points = a['activitySummary']['eliteQualifyingPointValue']
        ad.append(points)
        ad.append(points/10)
        qn = a['activityDetails']['qualifyingNights']
        ad.append(qn)
        if points > 0:
            sum += points/10
            nights += qn
            ic_stays.append(ad)

print(tabulate.tabulate(ic_stays, headers=headers))
print("Total spend: USD {:.2f}".format(sum))
print("Total qualifying nights: {:d}".format(nights))
