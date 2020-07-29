#!/bin/bash
set -e
if [ ! -f 'bot.py' ]; then
  echo 'Only run from within the dir'
  exit 1
fi
if [ ! -f 'settings.py' ]; then
  cp settings.example settings.py
  echo 'Please edit the config file: settings.py'
  exit 1
fi
if [ ! -d "venv" ]; then
  virtualenv --python=python3 venv
fi
source venv/bin/activate
pip3 install -r setup/requirements.txt
./bot.py

