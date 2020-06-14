import pandas
import numpy
from ia_test import *
import configparser
from ia_prod import *
import json

config = configparser.ConfigParser()
config.read('app.ini')

json_file = open(config.get('input_folder','path_db_all') + 'odds.json')
data = json.load(json_file)
l_cote_dom_min = []
l_cote_nulle_min = []
l_cote_ext_min = []
l_cote_dom_max = []
l_cote_nulle_max = []
l_cote_ext_max = []
l_cote_dom_mean = []
l_cote_nulle_mean = []
l_cote_ext_mean = []
l_cote_dom_pinnacle = []
l_cote_nulle_pinnacle = []
l_cote_ext_pinnacle = []
l_home_team = []
l_away_team = []
l_country = []
for d in data:
    cotes = d['odds']
    cote_dom_min = 1000
    cote_nulle_min = 1000
    cote_ext_min = 1000
    cote_dom_max = 0
    cote_nulle_max = 0
    cote_ext_max = 0
    cote_dom_mean = 0
    cote_nulle_mean = 0
    cote_ext_mean = 0
    cote_dom_pinnacle = 0
    cote_nulle_pinnacle = 0
    cote_ext_pinnacle = 0
    for c in cotes:
        cote_dom_min = min(cote_dom_min,c['odd_1'])
        cote_nulle_min = min(cote_nulle_min,c['odd_X'])
        cote_ext_min = min(cote_ext_min,c['odd_2'])
        cote_dom_max = max(cote_dom_max,c['odd_1'])
        cote_nulle_max = max(cote_nulle_max,c['odd_X'])
        cote_ext_max = max(cote_ext_max,c['odd_2'])
        cote_dom_mean = cote_dom_mean + c['odd_1'] / len(cotes)
        cote_nulle_mean = cote_nulle_mean + c['odd_X'] / len(cotes)
        cote_ext_mean = cote_ext_mean + c['odd_2'] / len(cotes)
        if c['bookmaker'] == 'Pinnacle':
            cote_dom_pinnacle = c['odd_1']
            cote_nulle_pinnacle = c['odd_X']
            cote_ext_pinnacle = c['odd_2']
    if cote_dom_pinnacle * cote_nulle_pinnacle * cote_ext_pinnacle == 0:
        cote_dom_pinnacle = cote_dom_mean
        cote_nulle_pinnacle = cote_nulle_mean
        cote_ext_pinnacle = cote_ext_mean
    if cote_dom_max * cote_nulle_max * cote_ext_max > 0:
        l_cote_dom_min.append(cote_dom_min)
        l_cote_nulle_min.append(cote_nulle_min)
        l_cote_ext_min.append(cote_ext_min)
        l_cote_dom_max.append(cote_dom_max)
        l_cote_nulle_max.append(cote_nulle_max)
        l_cote_ext_max.append(cote_ext_max)
        l_cote_dom_mean.append(cote_dom_mean)
        l_cote_nulle_mean.append(cote_nulle_mean)
        l_cote_ext_mean.append(cote_ext_mean)
        l_cote_dom_pinnacle.append(cote_dom_pinnacle)
        l_cote_nulle_pinnacle.append(cote_nulle_pinnacle)
        l_cote_ext_pinnacle.append(cote_ext_pinnacle)
        l_home_team.append(d['home_team'])
        l_away_team.append(d['away_team'])
        l_country.append(d['country'])
db_prod = pandas.DataFrame()
db_prod['cote_dom_min'] = l_cote_dom_min
db_prod['cote_nulle_min'] = l_cote_nulle_min
db_prod['cote_ext_min'] = l_cote_ext_min
db_prod['cote_dom_mean'] = l_cote_dom_mean
db_prod['cote_nulle_mean'] = l_cote_nulle_mean
db_prod['cote_ext_mean'] = l_cote_ext_mean
db_prod['cote_dom_max'] = l_cote_dom_max
db_prod['cote_nulle_max'] = l_cote_nulle_max
db_prod['cote_ext_max'] = l_cote_ext_max
db_prod['ratio_cotes_min'] = numpy.array(db_prod['cote_dom_min']) / numpy.array(db_prod['cote_ext_min'])
db_prod['ratio_cotes_mean'] = numpy.array(db_prod['cote_dom_mean']) / numpy.array(db_prod['cote_ext_mean'])
db_prod['ratio_cotes_max'] = numpy.array(db_prod['cote_dom_max']) / numpy.array(db_prod['cote_ext_max'])
db_team_prod = pandas.DataFrame()
db_team_prod['home_team'] = l_home_team
db_team_prod['away_team'] = l_away_team
db_team_prod['country'] = l_country
db_cote_prod = pandas.DataFrame()
db_cote_prod['cote_dom_pinnacle'] = l_cote_dom_pinnacle
db_cote_prod['cote_nulle_pinnacle'] = l_cote_nulle_pinnacle
db_cote_prod['cote_ext_pinnacle'] = l_cote_ext_pinnacle
db = pandas.read_csv(config.get('input_folder','path_db_all') + 'db.csv',sep = ';',engine = 'python')
ia = ia_prod(db = db,
            db_prod = db_prod,
            db_team_prod = db_team_prod,
            db_cote_prod = db_cote_prod,
            col_y = 'res',
            col_cote_dom = 'cote_dom_pinnacle',
            col_cote_nulle = 'cote_nulle_pinnacle',
            col_cote_ext = 'cote_ext_pinnacle',
            type_model = 'logit',
            config = config)
ia.prediction()
