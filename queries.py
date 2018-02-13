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
    COMMENT TEXT NOT NULL,
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
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'SELECT name, comment FROM KOKEN WHERE date="%s" ORDER BY ID DESC' % datum
  cur.execute(query)
  regel = cur.fetchone()
  con.commit()
  con.close()
  naam = ONBEKEND
  opmerking = ''
  if regel:
    naam = regel[0]
    opmerking = regel[1]
  return {
    'naam': naam,
    'opmerking': opmerking,
  }

def get_kokers(startdatum, einddatum):
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'SELECT date, name, comment FROM KOKEN WHERE date BETWEEN "%s" AND "%s" GROUP BY date ORDER BY ID DESC' % (startdatum, einddatum)
  cur.execute(query)
  kokers = cur.fetchall()
  con.commit()
  con.close()
  return kokers

def op_slaan(naam, opmerking, datum):
  logging.info('opslaan [%s] [%s] [%s]' % (naam, opmerking, datum))
  con = sqlite3.connect('bot.db')
  cur = con.cursor()
  query = 'INSERT INTO KOKEN (name,comment,date) VALUES (:name, :comment, :date);'
  cur.execute(query, {
    'name': naam,
    'comment': opmerking,
    'date': datum
  })
  con.commit()
  con.close()

