import pandas
import numpy
from ia_test import *
import configparser
from ia_prod import *
import json

config = configparser.ConfigParser()
config.read('C:\\road_for_the_future\\dev\\app.ini')

db_prod = pandas.read_csv('C:\\oddsportal\\cotes.csv', sep = ';', engine = 'python')
db_prod['ratio_cotes_min'] = numpy.array(db_prod['cote_dom_min']) / numpy.array(db_prod['cote_ext_min'])
db_prod['ratio_cotes_mean'] = numpy.array(db_prod['cote_dom_mean']) / numpy.array(db_prod['cote_ext_mean'])
db_prod['ratio_cotes_max'] = numpy.array(db_prod['cote_dom_max']) / numpy.array(db_prod['cote_ext_max'])
db_team_prod = pandas.DataFrame()
db_team_prod['home_team'] = numpy.array(db_prod['home_team'])
db_team_prod['away_team'] = numpy.array(db_prod['away_team'])
db_team_prod['country'] = ''
db = pandas.read_csv(config.get('input_folder','path_db_all') + 'db.csv',sep = ';',engine = 'python')
ia = ia_prod(db = db,
            db_prod = db_prod,
            db_team_prod = db_team_prod,
            db_cote_prod = db_prod,
            col_y = 'res',
            col_cote_dom = 'pinnacle_dom',
            col_cote_nulle = 'pinnacle_nulle',
            col_cote_ext = 'pinnacle_ext',
            type_model = 'logit',
            config = config)
ia.prediction()
