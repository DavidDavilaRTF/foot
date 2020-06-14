import configparser
from database_build import *
from database_all_seasons import *

config = configparser.ConfigParser()
config.read('app.ini')
fichier = ['9394','9495','9596','9697','9798','9899','9900','0001','0102','0203','0304',
            '0405','0506','0607','0708','0809','0910','1011','1112','1213','1314','1415',
            '1516','1617','1718','1819','1920']
for f in fichier:
    db = database_build('https://www.football-data.co.uk/mmz4281/' + f + '/data.zip',config,f + '.csv')
    db.telechargement()
    db.create_db()
db = database_all_seasons(config)
db.create_database()
