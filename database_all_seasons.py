import pandas
import numpy
import os
import configparser

class database_all_seasons:
    def __init__(self,config):
        self.config = config
        self.db = pandas.DataFrame()
    
    def create_database(self):
        fichiers = os.listdir(self.config.get('input_folder','path_db'))
        for f in fichiers:
            db_temp = pandas.read_csv(self.config.get('input_folder','path_db') + f,sep = ';',engine = 'python')
            self.db = self.db.append(db_temp)
        no_cote = self.db['no_cote'] == 0
        self.db = self.db[no_cote]
        self.db = self.db.drop('no_cote',axis = 1)
        sel_cotes_true = numpy.array(self.db['cote_dom_max'] / self.db['cote_dom_mean'] < 1.5)
        sel_cotes_true = sel_cotes_true * numpy.array(self.db['cote_nulle_max'] / self.db['cote_nulle_mean'] < 1.5)
        sel_cotes_true = sel_cotes_true * numpy.array(self.db['cote_ext_max'] / self.db['cote_ext_mean'] < 1.5)
        self.db = self.db[sel_cotes_true]
        self.db.index = range(len(self.db))
        self.db.to_csv(self.config.get('input_folder','path_db_all') + 'db.csv',index = False,sep = ';')
