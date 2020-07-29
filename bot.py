#!/usr/bin/env python3
#By Apie, 2017
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import sqlite3
import datetime
import logging
import sys
from ownbot.auth import requires_usergroup, assign_first_to
from ownbot.admincommands import AdminCommands

from utils import *
from queries import *
from ical import *
from settings import API_KEY
try:
    from settings import CC_ID
except:
    CC_ID = None

log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

APART = 'Apart'
S_DEELNEMERS, S_DAG, S_BEVESTIGEN, S_OPMERKING, S_OPSLAAN = range(5)

@assign_first_to("admin")
@requires_usergroup("user")
def start(bot, update):
  logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  update.message.reply_text('''Met /wie <dag> vraag je op wie er gaat koken.
Met /overzicht krijg je een overzicht van wie er deze week gaat koken.
Met /ikke krijg je een interactieve sessie om aan te geven wanneer je gaat koken.
''')

@requires_usergroup("user")
def hello(bot, update):
  logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  reply_text = 'Hallo {}'.format(update.message.from_user.first_name)
  logging.info('>> %s' % reply_text)
  update.message.reply_text(reply_text)

@requires_usergroup("user")
def wiekookter(bot, update):
  logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  error = False
  datum = datetime.datetime.now().date()
  if 'vandaag' in update.message.text or update.message.text == '/wie':
    daystr = 'vandaag'
  elif 'overmorgen' in update.message.text:
    datum += datetime.timedelta(days=2)
    daystr = 'overmorgen'
  elif 'morgen' in update.message.text:
    datum += datetime.timedelta(days=1)
    daystr = 'morgen'
  else:
    error = True
  # todo weekdagen / data
  if not error:
    koker = get_koker(datum)
    logging.info(koker)
    opmerking = None
    if koker['naam'] == ONBEKEND:
        reply_text = '%s kookt er nog niemand.' % daystr.capitalize()
    elif koker['naam'] == APART:
        reply_text = '%s koken we allebei zelf.' % daystr.capitalize()
        opmerking = koker['opmerking']
    else:
        reply_text = '%s kookt %s.' % (daystr.capitalize(), koker['naam'])
        opmerking = koker['opmerking']
    if opmerking:
        reply_text = '\r\n'.join([reply_text, 'Opmerking: %s' % opmerking])
    logging.info('>> %s' % reply_text)
    update.message.reply_text(reply_text)
  else:
    update.message.reply_text('Ik begreep je vraag niet.')

@requires_usergroup("user")
def overzicht(bot, update):
  logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  error = False
  startdatum = datetime.datetime.now().date()
  einddatum = startdatum
  einddatum += datetime.timedelta(days=6)
  kokers = get_kokers(startdatum, einddatum)
  if not kokers:  # of alles is ONBEKEND TODO
    reply_text = 'Er kookt de hele week nog niemand.'
  else:
    kokersdict = dict()
    for datum, naam, opmerking in kokers:
      kokersdict[datum] = {
        'naam': naam,
        'opmerking': opmerking,
      }
    reply_text = []
    datum = startdatum
    for dag in range(7):
        datumstr = str(datum)
        if datumstr not in kokersdict:
           naam = ONBEKEND
        else:
          naam = kokersdict[datumstr]['naam']
          opmerking_tekst = ''
          opmerking = kokersdict[datumstr]['opmerking']
          if opmerking != '':
            opmerking_tekst = '(%s)' % opmerking
        if dag in range(3):
            daystr = get_relative_daystr(dag)
        else:
            daystr = weekday_to_daystr(datum.isoweekday())
        if naam == ONBEKEND:
            reply_text += ['%s kookt er nog niemand' % daystr.capitalize()]
        elif naam == APART:
            reply_text += ['%s koken we allebei zelf %s' % (daystr.capitalize(), opmerking_tekst)]
        else:
            reply_text += ['%s kookt %s %s' % (daystr.capitalize(), naam, opmerking_tekst)]
        datum += datetime.timedelta(days=1)
    reply_text = "\r\n".join(reply_text)
  logging.info('>> %s' % reply_text)
  update.message.reply_text(reply_text)

def alarm(bot, job):
    """Send the alarm message."""
    reply_text = 'Beep!'
    logging.info('>> %s' % reply_text)
    bot.send_message(job.context, text=reply_text)

@requires_usergroup("user")
def set_timer(bot, update, arg, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(arg)
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job
        reply_text = 'Timer successfully set!'
        logging.info('>> %s' % reply_text)
        update.message.reply_text(reply_text)

    except (IndexError, ValueError):
        reply_text = 'Usage: /set <seconds>'
        logging.info('>> %s' % reply_text)
        update.message.reply_text(reply_text)

@requires_usergroup("user")
def logmessage(bot, update, job_queue, chat_data):
  logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  if update.message.text == 'hoi':
    hello(bot, update)
  elif update.message.text[:4] == 'set ' or update.message.text[:4] == 'Set ':
    args = update.message.text.split()
    try:
      arg = args[1]
      set_timer(bot, update, arg, job_queue, chat_data)
    except:
      logging.warn('Geen argument opgegeven')

@requires_usergroup("user")
def ikke(bot, update):
    logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['Apart', 'Samen']]

    reply_text = 'Gaan jullie apart eten of samen?\r\nGeef /cancel om te annuleren.'
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return S_DEELNEMERS

@requires_usergroup("user")
def deelnemers(bot, update, user_data):
    logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    user_data['deelnemers'] = update.message.text
    daystrl = get_daystrlist()
    reply_keyboard = [daystrl[:4], daystrl[-3:]]

    zelf_str = ''
    if user_data['deelnemers'] == APART:
      zelf_str = 'voor jezelf '
    reply_text = 'Op welke dag wil je %skoken %s?\r\nGeef /cancel om te annuleren.' % (zelf_str, update.message.from_user.first_name)
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return S_DAG

@requires_usergroup("user")
def bevestigen(bot, update, user_data):
    logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['Ja', 'Nee', 'Weghalen']]

    naam = update.message.from_user.first_name
    dagje = update.message.text
    user_data['dag'] = dagje.lower()
    datum = daystrtodate(dagje.lower())
    logging.info('datum:: %s' % datum)
    if not datum:
      reply_text = 'Ik begreep deze dag niet: %s' % dagje.lower()
      update.message.reply_text(reply_text)
      return
    user_data['datum'] = str(datum)
    koker = get_koker(datum)
    logging.info(koker)
    if koker['naam'] == ONBEKEND:
      zelf_str = ''
      if user_data['deelnemers'] == APART:
        zelf_str = 'voor jezelf '
      reply_text = 'Ik ga opslaan dat je %s %sgaat koken. Klopt dat?' % (dagje.lower(), zelf_str)
    else:
      reply_text = '%s kookt %s al! Toch opslaan?' % (dagje, koker['naam'])
    update.message.reply_text(reply_text,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return S_BEVESTIGEN

def vraag_opmerking(bot, update, user_data):
    logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    logging.info('in vraag_opmerking')
    user_data['opslaan'] = update.message.text
    if update.message.text == 'Ja':
        logging.info('opmerking vragen')
        reply_text = 'Wil je een opmerking toevoegen?'
        reply_keyboard = [['Ja', 'Nee']]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return S_OPMERKING
    elif update.message.text == 'Weghalen':
        logging.info('geen opmerking vragen want weghalen')
        return nu_opslaan(bot, update, user_data)
    elif update.message.text == 'Nee':
        logging.info('geen opmerking vragen want nee')
        return het_einde(bot, update)

def plaats_opmerking(bot, update, user_data):
    logging.info('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    logging.info('in plaats_opmerking')
    user_data['opmerking'] = False
    if update.message.text == 'Ja':
        logging.info('opmerking plaatsen.')
        reply_text = 'Geef de opmerking maar.'
        user_data['opmerking'] = True
        update.message.reply_text(reply_text,
                                  reply_markup=ReplyKeyboardRemove())
        return S_OPSLAAN
    else:
        return nu_opslaan(bot, update, user_data)

def nu_opslaan(bot, update, user_data):
    logging.info('in nu_opslaan')
    if user_data['deelnemers'] == 'Samen':
        naam = update.message.from_user.first_name
    else:
        naam = APART

    opmerking = ''
    if user_data['opslaan'] == 'Ja':
      if user_data['opmerking']:
          opmerking = update.message.text
      reply_text = 'Opgeslagen!'
    elif user_data['opslaan'] == 'Weghalen':
      naam = ONBEKEND
      reply_text = 'Weggehaald!'

    if user_data['opslaan'] != 'Nee':
      logging.info('echt opslaan')
      logging.info(naam)
      logging.info(opmerking)
      op_slaan(naam, opmerking, user_data['datum'])
      generate_ical()
      if CC_ID:
          bot.send_message(chat_id=CC_ID,
            text='[%s] Opslaan: %s, %s, %s' % (update.message.from_user.first_name, naam, opmerking, user_data['datum']))
      update.message.reply_text(reply_text)

    return het_einde(bot, update)

def het_einde(bot, update):
    update.message.reply_text('Dat was het!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# conversation cancel
def cancel(bot, update):
    logging.info('in cancel')
    user = update.message.from_user
    logging.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Tot ziens.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(bot, update, error):
  logging.info('received: %s' % update.message.text)
  logging.error('error: %s' % error)
 
if __name__ == '__main__':
  if not init_db():
    exit(1)
  updater = Updater(API_KEY)

  updater.dispatcher.add_handler(CommandHandler('start', start))
  updater.dispatcher.add_handler(CommandHandler('hello', hello))
  updater.dispatcher.add_handler(CommandHandler('wie', wiekookter))
  updater.dispatcher.add_handler(CommandHandler('overzicht', overzicht))
  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('ikke', ikke)],
      states={
          S_DEELNEMERS: [RegexHandler('^(Apart|Samen)$', deelnemers, pass_user_data=True)],
          S_DAG: [RegexHandler('^(Vandaag|Morgen|Overmorgen|Maandag|Dinsdag|Woensdag|Donderdag|Vrijdag|Zaterdag|Zondag)$', bevestigen, pass_user_data=True)],
          S_BEVESTIGEN: [RegexHandler('^(Ja|Nee|Weghalen)$', vraag_opmerking, pass_user_data=True)],
          S_OPMERKING: [RegexHandler('^(Ja|Nee)$', plaats_opmerking, pass_user_data=True)],
          S_OPSLAAN: [MessageHandler(Filters.text, nu_opslaan, pass_user_data=True)]
      },
      fallbacks=[CommandHandler('cancel', cancel)]
  )
  updater.dispatcher.add_handler(conv_handler)

  updater.dispatcher.add_handler(MessageHandler(Filters.text, logmessage, pass_job_queue=True, pass_chat_data=True))

  updater.dispatcher.add_error_handler(error)
  AdminCommands(updater.dispatcher)

  updater.start_polling()
  updater.idle()

