#!/usr/bin/python3
# -*- coding: UTF-8

import json
import pprint
import sys
import tabulate

data = json.load(open(sys.argv[1]))

headers = ('Date', 'Description', 'Activity')
summary = []

for a in data['activities']:
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
    summary.append(ad)

print(tabulate.tabulate(summary, headers=headers))


print()
print()
print('IC Stays')

headers = ('Date', 'Description', 'EQP', 'USD')
ic_stays = []
sum = 0

for a in data['activities']:
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
        sum += points/10
        if points > 0:
            ic_stays.append(ad)

print(tabulate.tabulate(ic_stays, headers=headers))
print("Total spend: %f" % (sum))
