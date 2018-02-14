#!/usr/bin/env python3
import pytz
import os
from icalendar import *
import datetime

import queries
from utils import ONBEKEND

def generate_ical():
  tzinfo = pytz.timezone('Europe/Amsterdam')
  kokers = queries.get_kokers(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=7))
  cal = Calendar()

  for koker in sorted(kokers, key=lambda x:x[0]):
    datum = koker[0]
    naam = koker[1]
    opmerking = koker[2]
    if naam == ONBEKEND:
      continue
    event = Event()
    datumtype = datetime.datetime.strptime(datum, '%Y-%m-%d')
    event.add('summary', '%s kookt' % naam)
    event.add('location', naam)
    event.add('description', opmerking)
    event.add('dtstart', datetime.datetime(year=datumtype.year, month=datumtype.month, day=datumtype.day, hour=18, minute=0, second=0, tzinfo=tzinfo))
    event.add('dtend',   datetime.datetime(year=datumtype.year, month=datumtype.month, day=datumtype.day, hour=20, minute=0, second=0, tzinfo=tzinfo))
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

