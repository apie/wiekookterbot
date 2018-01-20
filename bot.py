#!/usr/bin/env python2
#By Apie, 2017
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import sqlite3
import datetime
from ownbot.auth import requires_usergroup, assign_first_to
from ownbot.admincommands import AdminCommands

from utils import *
from queries import *
from settings import API_KEY

APART = 'Apart'
DEELNEMERS, DAG, BEVESTIGEN = range(3)

@assign_first_to("admin")
@requires_usergroup("user")
def start(bot, update):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  update.message.reply_text('''Met /wie <dag> vraag je op wie er gaat koken.
Met /overzicht krijg je een overzicht van wie er deze week gaat koken.
Met /ikke krijg je een interactieve sessie om aan te geven wanneer je gaat koken.
''')

@requires_usergroup("user")
def hello(bot, update):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  reply_text = 'Hallo {}'.format(update.message.from_user.first_name)
  print '>>', reply_text
  update.message.reply_text(reply_text)

@requires_usergroup("user")
def wiekookter(bot, update):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
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
    naam = get_koker(datum)
    if naam == ONBEKEND:
        reply_text = '%s kookt er nog niemand.' % daystr.capitalize()
    elif naam == APART:
        reply_text = '%s koken we allebei zelf.' % daystr.capitalize()
    else:
        reply_text = '%s kookt %s.' % (daystr.capitalize(), naam)
    print '>>',reply_text
    update.message.reply_text(reply_text)
  else:
    update.message.reply_text('Ik begreep je vraag niet.')

@requires_usergroup("user")
def overzicht(bot, update):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  error = False
  startdatum = datetime.datetime.now().date()
  einddatum = startdatum
  einddatum += datetime.timedelta(days=6)
  kokers = get_kokers(startdatum, einddatum)
  if not kokers:  # of alles is ONBEKEND TODO
    reply_text = 'Er kookt de hele week nog niemand.'
  else:
    kokersdict = dict()
    for datum, naam in kokers:
      kokersdict[datum] = naam
    reply_text = []
    datum = startdatum
    for dag in range(7):
        datumstr = str(datum)
        if datumstr not in kokersdict:
           naam = ONBEKEND
        else:
          naam = kokersdict[datumstr]
        if dag in range(3):
            daystr = get_relative_daystr(dag)
        else:
            daystr = weekday_to_daystr(datum.isoweekday())
        if naam == ONBEKEND:
            reply_text += ['%s kookt er nog niemand.' % daystr.capitalize()]
        elif naam == APART:
            reply_text += ['%s koken we allebei zelf.' % daystr.capitalize()]
        else:
            reply_text += ['%s kookt %s.' % (daystr.capitalize(), naam)]
        datum += datetime.timedelta(days=1)
    reply_text = "\r\n".join(reply_text)
  print '>>', reply_text
  update.message.reply_text(reply_text)

@requires_usergroup("user")
def alarm(bot, job):
    """Send the alarm message."""
    reply_text = 'Beep!'
    print '>>', reply_text
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
        print '>>', reply_text
        update.message.reply_text(reply_text)

    except (IndexError, ValueError):
        reply_text = 'Usage: /set <seconds>'
        print '>>', reply_text
        update.message.reply_text(reply_text)

@requires_usergroup("user")
def logmessage(bot, update, job_queue, chat_data):
  print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
  if update.message.text == 'hoi':
    hello(bot, update)
  elif update.message.text[:4] == 'set ' or update.message.text[:4] == 'Set ':
    args = update.message.text.split()
    try:
      arg = args[1]
      set_timer(bot, update, arg, job_queue, chat_data)
    except:
      print 'Geen argument opgegeven'

@requires_usergroup("user")
def ikke(bot, update):
    print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['Apart', 'Samen']]

    reply_text = 'Gaan jullie apart eten of samen?\r\nGeef /cancel om te annuleren.'
    update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return DEELNEMERS

@requires_usergroup("user")
def deelnemers(bot, update, user_data):
    print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
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
    return DAG

@requires_usergroup("user")
def bevestigen(bot, update, user_data):
    print('received (%s): %s' % (update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['Ja', 'Nee', 'Weghalen']]

    naam = update.message.from_user.first_name
    dagje = update.message.text
    user_data['dag'] = dagje.lower()
    datum = daystrtodate(dagje.lower())
    print 'datum:: %s' % datum
    if not datum:
      reply_text = 'Ik begreep deze dag niet: %s' % dagje.lower()
      update.message.reply_text(reply_text)
      return
    user_data['datum'] = str(datum)
    naam = get_koker(datum)
    print(naam)
    if naam == ONBEKEND:
      zelf_str = ''
      if user_data['deelnemers'] == APART:
        zelf_str = 'voor jezelf '
      reply_text = 'Ik ga opslaan dat je %s %sgaat koken. Klopt dat?' % (dagje.lower(), zelf_str)
    else:
      reply_text = '%s kookt %s al! Toch opslaan?' % (dagje, naam)
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return BEVESTIGEN

def opslaan(bot, update, user_data):
    print('in opslaan')
    if user_data['deelnemers'] == 'Samen':
        naam = update.message.from_user.first_name
    else:
        naam = APART
    if update.message.text == 'Ja':
      op_slaan(naam, user_data['datum'])
      update.message.reply_text('Opgeslagen!')
    elif update.message.text == 'Weghalen':
      op_slaan(ONBEKEND, user_data['datum'])
      update.message.reply_text('Weggehaald!')
    update.message.reply_text('Dat was het!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# conversation cancel
def cancel(bot, update):
    print 'in cancel'
    user = update.message.from_user
    print("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Tot ziens.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(bot, update, error):
  print('received: %s' % update.message.text)
  print('error: %s' % error)
 
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
          DEELNEMERS: [RegexHandler('^(Apart|Samen)$', deelnemers, pass_user_data=True)],
          DAG: [RegexHandler('^(Vandaag|Morgen|Overmorgen|Maandag|Dinsdag|Woensdag|Donderdag|Vrijdag|Zaterdag|Zondag)$', bevestigen, pass_user_data=True)],
          BEVESTIGEN: [RegexHandler('^(Ja|Nee|Weghalen)$', opslaan, pass_user_data=True)]
      },
      fallbacks=[CommandHandler('cancel', cancel)]
  )
  updater.dispatcher.add_handler(conv_handler)

  updater.dispatcher.add_handler(MessageHandler(Filters.text, logmessage, pass_job_queue=True, pass_chat_data=True))

  updater.dispatcher.add_error_handler(error)
  AdminCommands(updater.dispatcher)

  updater.start_polling()
  updater.idle()

