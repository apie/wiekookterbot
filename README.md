# wiekookterbot
Wie kookt er?

Maak een bestand `settings.py` met daarin `API_KEY = 'key123'` Ze hierin de key van jouw bot. Start nu `bot.py`.

Je moet als eerste `/start` naar de bot sturen. Hierdoor word je aan de admin-groep toegevoegd en krijg je toegang tot de bot. Daarna kun je via `/adminhelp` andere gebruikers toegang geven tot de bot.

Het rooster wordt bijgehouden in een sqlite-database. Deze wordt automatisch aangemaakt. Er wordt ook een icalender bijgehouden van de komende week. Deze wordt na iedere wijziging bijgewerkt en staat in `ics/`.
