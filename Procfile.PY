if 'RAILWAY_STATIC_URL' in environ:
  web: python bot.py
    
else:
  worker: python bot.py
