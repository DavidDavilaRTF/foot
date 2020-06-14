import pandas
import numpy
import requests
from zipfile import ZipFile
import os
import configparser

class database_build:
    def __init__(self,lien_telechargement,config,path_csv):
        self.lien_telechargement = lien_telechargement
        self.col_cotes = ['BWH','BWD','BWA','IWH','IWD','IWA',
                        'LBH','LBD','LBA','PSH','PSD','PSA',
                        'WHH','WHD','WHA','SJH','SJD','SJA',
                        'VCH','VCD','VCA','GBH','GBD','GBA',
                        'SBH','SBD','SBA','B365H','B365D','B365H']
        self.db = pandas.DataFrame()
        self.db_build = pandas.DataFrame()
        self.config = config
        self.path_csv = path_csv
    
    def clean_cotes(self,x):
        try:
            return float('0' + str(x).lower())
        except:
            return 0

    def moyenne_cotes(self,x):
        val = pandas.DataFrame(numpy.array(x))
        nb_diff_0 = numpy.array(val != 0)
        return numpy.sum(numpy.array(val)) / numpy.sum(nb_diff_0)

    def min_cotes(self,x):
        val = pandas.DataFrame(numpy.array(x))
        nb_diff_0 = numpy.array(val != 0)
        if sum(nb_diff_0) > 0:
            val = val[nb_diff_0]
            return numpy.min(numpy.array(val))
        return 0
    
    def select_nan(self,x):
        for c in x:
            try:
                int(c)
            except:
                return False
            return True

    def resultats(self):
        sel_nan = numpy.array(self.db[['FTHG','FTAG']].apply(lambda x: self.select_nan(x),axis = 1))
        self.db = self.db[sel_nan]
        self.db.index = range(len(self.db))
        self.db[['FTHG','FTAG']] = self.db[['FTHG','FTAG']].apply(lambda x: x.apply(lambda y: int(y)))
        self.db_build['res'] = self.db['FTHG'] - self.db['FTAG']
        vict = numpy.array(self.db_build['res'] > 0)
        self.db_build['res'][vict] = 1
        deft = numpy.array(self.db_build['res'] < 0)
        self.db_build['res'][deft] = -1

    def op_cotes(self):
        for c in self.col_cotes:
            try:
                self.db[c] = self.db[c].apply(lambda x: self.clean_cotes(x))
            except:
                self.db[c] = 0
        self.db_build['cote_dom_min'] = self.db[self.col_cotes[::3]].apply(lambda x: self.min_cotes(x),axis = 1)
        self.db_build['cote_nulle_min'] = self.db[self.col_cotes[1::3]].apply(lambda x: self.min_cotes(x),axis = 1)
        self.db_build['cote_ext_min'] = self.db[self.col_cotes[2::3]].apply(lambda x: self.min_cotes(x),axis = 1)
        self.db_build['cote_dom_mean'] = self.db[self.col_cotes[::3]].apply(lambda x: self.moyenne_cotes(x),axis = 1)
        self.db_build['cote_nulle_mean'] = self.db[self.col_cotes[1::3]].apply(lambda x: self.moyenne_cotes(x),axis = 1)
        self.db_build['cote_ext_mean'] = self.db[self.col_cotes[2::3]].apply(lambda x: self.moyenne_cotes(x),axis = 1)
        self.db_build['cote_dom_max'] = self.db[self.col_cotes[::3]].apply(lambda x: numpy.max(x),axis = 1)
        self.db_build['cote_nulle_max'] = self.db[self.col_cotes[1::3]].apply(lambda x: numpy.max(x),axis = 1)
        self.db_build['cote_ext_max'] = self.db[self.col_cotes[2::3]].apply(lambda x: numpy.max(x),axis = 1)
        self.db_build['no_cote'] = 0
        self.db_build['ratio_cotes_min'] = numpy.array(self.db_build['cote_dom_min']) / numpy.array(self.db_build['cote_ext_min'])
        self.db_build['ratio_cotes_mean'] = numpy.array(self.db_build['cote_dom_mean']) / numpy.array(self.db_build['cote_ext_mean'])
        self.db_build['ratio_cotes_max'] = numpy.array(self.db_build['cote_dom_max']) / numpy.array(self.db_build['cote_ext_max'])
        no_cotes = numpy.array(self.db_build['cote_ext_max'] == 0)
        if sum(no_cotes) > 0:
            self.db_build['no_cote'][no_cotes] = 1
            self.db_build['ratio_cotes_min'][no_cotes] = 0
            self.db_build['ratio_cotes_mean'][no_cotes] = 0
            self.db_build['ratio_cotes_max'][no_cotes] = 0
            self.db_build['cote_dom_mean'][no_cotes] = 0
            self.db_build['cote_nulle_mean'][no_cotes] = 0
            self.db_build['cote_ext_mean'][no_cotes] = 0

    def telechargement(self):
        r = requests.get(self.lien_telechargement)
        fichier_zip = open(self.config.get('input_folder','path') + 'f.zip','wb')
        fichier_zip.write(r.content)
        fichier_zip.close()
        fichier_zip = ZipFile(self.config.get('input_folder','path') + 'f.zip','r')
        fichier_zip.extractall(self.config.get('input_folder','path'))
        fichier_zip.close()
        os.remove(self.config.get('input_folder','path') + 'f.zip')

    def create_db(self):
        fichiers = os.listdir(self.config.get('input_folder','path'))
        try:
            os.remove(self.config.get('input_folder','path_db') + self.path_csv)
        except:
            pass
        for f in fichiers:
            try:
                self.db = pandas.read_csv(self.config.get('input_folder','path') + f,sep = ',',engine = 'python')
                self.resultats()
                self.op_cotes()
                try:
                    db_temp = pandas.read_csv(self.config.get('input_folder','path_db') + self.path_csv,sep = ';',engine = 'python')
                    self.db_build = self.db_build.append(db_temp)
                except:
                    pass
                self.db_build.to_csv(self.config.get('input_folder','path_db') + self.path_csv,index = False,sep = ';')
                self.db = pandas.DataFrame()
                self.db_build = pandas.DataFrame()
            except:
                pass
            os.remove(self.config.get('input_folder','path') + f)
