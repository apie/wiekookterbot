#!/usr/bin/env python2
import datetime
ONBEKEND = '<Onbekend>'

def weekday_to_daystr(weekday):
  if weekday == 1:
    return 'maandag'
  elif weekday == 2:
    return 'dinsdag'
  elif weekday == 3:
    return 'woensdag'
  elif weekday == 4:
    return 'donderdag'
  elif weekday == 5:
    return 'vrijdag'
  elif weekday == 6:
    return 'zaterdag'
  elif weekday == 7:
    return 'zondag'
  else:
    return None

def get_relative_daystr(dagnr):
  if dagnr == 0:
    return 'vandaag'
  elif dagnr == 1:
    return 'morgen'
  elif dagnr == 2:
    return 'overmorgen'
  else:
    return None

def get_daystrlist():
  startdatum = datetime.datetime.now().date()
  datum = startdatum
  daystrlist = []
  for dag in range(7):
      datumstr = str(datum)
      if dag in range(3):
          daystr = get_relative_daystr(dag)
      else:
          daystr = weekday_to_daystr(datum.isoweekday())
      daystrlist.append(daystr.capitalize())
      datum += datetime.timedelta(days=1)
  return daystrlist

def daystrtodate(dag_je):
  startdatum = datetime.datetime.now().date()
  datum = startdatum
  daystrlist = []
  for dag in range(7):
      datumstr = str(datum)
      if dag in range(3):
          daystr = get_relative_daystr(dag)
      else:
          daystr = weekday_to_daystr(datum.isoweekday())
      if dag_je == daystr:
        return datum
      datum += datetime.timedelta(days=1)
  return None

