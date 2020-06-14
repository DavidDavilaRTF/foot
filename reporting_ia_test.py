import pandas
import numpy
from ia_test import *
import configparser

config = configparser.ConfigParser()
config.read('app.ini')

db = pandas.read_csv(config.get('input_folder','path_db_all') + 'db.csv',sep = ';',engine = 'python')
ia = ia_test(db = db,
            pct_test = 0.1,
            col_y = 'res',
            col_cote_dom = 'cote_dom_mean',
            col_cote_nulle = 'cote_nulle_mean',
            col_cote_ext = 'cote_ext_mean',
            nb_cv = 100,
            type_model = 'logit',
            config = config)
ia.simulation()
