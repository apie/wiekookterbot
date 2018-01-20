#!/usr/bin/env python3
import sqlite3
import logging
from utils import ONBEKEND

def init_db():
  try:
    con = sqlite3.connect('bot.db')
    cur = con.cursor()
    query = """CREATE TABLE IF NOT EXISTS KOKEN
    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    DATE TEXT NOT NULL)
    """
    cur.execute(query)
    con.commit()
    con.close()
    return True
  except:
    logging.error('Could not create database')
    return False

def get_koker(datum):
  logging.info('in get_koker')
  logging.info(datum)
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'SELECT name FROM KOKEN WHERE date="%s" ORDER BY ID DESC' % datum
  cur.execute(query)
  naam = cur.fetchone()
  con.commit()
  con.close()
  if naam:
    naam = naam[0]
  else:
    naam = ONBEKEND
  logging.info(naam)
  return naam

def get_kokers(startdatum, einddatum):
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'SELECT date, name FROM KOKEN WHERE date BETWEEN "%s" AND "%s" GROUP BY date ORDER BY ID DESC' % (startdatum, einddatum)
  cur.execute(query)
  kokers = cur.fetchall()
  con.commit()
  con.close()
  return kokers

def op_slaan(naam, datum):
  logging.info('opslaan %s %s' % (naam, datum))
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'INSERT INTO KOKEN (name,date) VALUES ("%s", "%s");' % (naam, datum)
  cur.execute(query)
  con.commit()
  con.close()

