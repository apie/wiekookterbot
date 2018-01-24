#!/usr/bin/env python3
import pytz
import os
from icalendar import *
import datetime

import queries

def generate_ical():
  tzinfo = pytz.timezone('Europe/Amsterdam')
  kokers = queries.get_kokers(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=7))
  cal = Calendar()

  for koker in sorted(kokers, key=lambda x:x[0]):
    event = Event()
    datum = koker[0]
    naam = koker[1]
    datumtype = datetime.datetime.strptime(datum, '%Y-%M-%d')
    event.add('summary', '%s kookt' % naam)
    event.add('dtstart', datetime.datetime(datumtype.year, datumtype.month, datumtype.day, 18, 0, 0, tzinfo=tzinfo))
    event.add('dtend',   datetime.datetime(datumtype.year, datumtype.month, datumtype.day, 20, 0, 0, tzinfo=tzinfo))
    event.add('dtstamp', datetime.datetime.now())
    event.add('uid', '%s%s' % (naam, datum))

    cal.add_component(event)

  directory = 'ics/'
  if not os.path.isdir(directory):
    os.mkdir(directory)
  with open(os.path.join(directory, 'kokers.ics'), 'wb') as f:
    f.write(cal.to_ical())

if __name__ == '__main__':
  generate_ical()

