import configparser
from database_build import *
from database_all_seasons import *

config = configparser.ConfigParser()
config.read('app.ini')
f = '1920'
db = database_build('https://www.football-data.co.uk/mmz4281/' + f + '/data.zip',config,f + '.csv')
db.telechargement()
db.create_db()
db = database_all_seasons(config)
db.create_database()
