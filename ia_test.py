import pandas
import numpy
from sklearn import linear_model,neighbors,svm,preprocessing,tree,ensemble

class ia_test:
    def __init__(self,db,pct_test,col_y,col_cote_dom,col_cote_nulle,col_cote_ext,nb_cv,type_model,config):
        self.pct_test = pct_test
        self.col_y = col_y
        self.col_cote_dom = col_cote_dom
        self.col_cote_ext = col_cote_ext
        self.col_cote_nulle = col_cote_nulle
        self.y = db[[self.col_y]]
        self.x = db.drop(col_y,axis = 1)
        self.col_x = self.x.columns
        self.succes = pandas.DataFrame()
        self.gains = pandas.DataFrame()
        self.nb_detecte = pandas.DataFrame()
        self.nb_tot = pandas.DataFrame()
        self.succes_i = pandas.DataFrame()
        self.gains_i = pandas.DataFrame()
        self.nb_detecte_i = pandas.DataFrame()
        self.nb_tot_i = pandas.DataFrame()
        self.nb_cv = nb_cv
        self.bet = self.x[[self.col_cote_dom,self.col_cote_nulle,self.col_cote_ext]]
        self.x_train = pandas.DataFrame()
        self.x_test = pandas.DataFrame()
        self.y_train = pandas.DataFrame()
        self.y_test = pandas.DataFrame()
        self.bet_test = pandas.DataFrame()
        self.type_model = type_model
        self.config = config

    def standardization(self):
        scaler = preprocessing.StandardScaler()
        scaler.fit(self.x)
        self.x = scaler.transform(self.x)
        self.x = pandas.DataFrame(self.x)
        self.x.columns = self.col_x
    
    def train_test(self):
        sel_train = numpy.random.choice(range(len(self.x)),size = int((1 - self.pct_test) * len(self.x)),replace = False)
        self.x_train = self.x.iloc[sel_train]
        self.x_train.index = numpy.array(range(len(self.x_train)))
        self.x_test = self.x.drop(sel_train,axis = 0)
        self.x_test.index = numpy.array(range(len(self.x_test)))
        self.y_train = self.y.iloc[sel_train]
        self.y_train.index = range(len(self.y_train))
        self.y_test = self.y.drop(sel_train,axis = 0)
        self.y_test.index = range(len(self.y_test))
        self.bet_test = self.bet.drop(sel_train,axis = 0)
        self.bet_test.index = range(len(self.bet_test))

    def simulation(self):
        nb_label = numpy.array(self.y[self.col_y].unique())
        nb_label = numpy.sort(nb_label)
        for l in nb_label:
            self.succes[l] = [0]
            self.gains[l] = [0]
            self.nb_detecte[l] = [0]
            self.nb_tot[l] = [0]
        self.standardization()
        for i in range(self.nb_cv):
            self.train_test()
            y_train_sans_modifier = self.y_train.copy()
            y_test_sans_modifier = self.y_test.copy()
            for l in nb_label:
                sel_label = numpy.array(y_train_sans_modifier[self.col_y] == l)
                sel_no_label = numpy.array(y_train_sans_modifier[self.col_y] != l)
                self.y_train[self.col_y][sel_label] = 1
                self.y_train[self.col_y][sel_no_label] = 0
                sel_label = numpy.array(y_test_sans_modifier[self.col_y] == l)
                sel_no_label = numpy.array(y_test_sans_modifier[self.col_y] != l)
                self.y_test[self.col_y][sel_label] = 1
                self.y_test[self.col_y][sel_no_label] = 0

                if self.type_model == 'logit':
                    model = linear_model.LogisticRegression()
                elif self.type_model == 'tree':
                    model = tree.DecisionTreeClassifier()
                elif self.type_model == 'rf':
                    model = ensemble.RandomForestClassifier()
                elif self.type_model == 'knn':
                    model = neighbors.KNeighborsClassifier()
                model.fit(self.x_train,self.y_train)
                pr = numpy.array(model.predict_proba(self.x_test)[:,1])

                if l == -1:
                    col_cote = self.col_cote_ext
                elif l == 0:
                    col_cote = self.col_cote_nulle
                elif l == 1:
                    col_cote = self.col_cote_dom

                opp = pandas.DataFrame(pr * numpy.array(self.bet_test[col_cote]))
                sel_opp = numpy.array(opp[opp.columns[0]] > 1)
                sel_succes = numpy.array(self.y_test[self.col_y] == 1)
                sel_opp = sel_opp
                self.succes[l].iloc[0] = self.succes[l].iloc[0] + numpy.sum(sel_opp * sel_succes)
                self.gains[l].iloc[0] = self.gains[l].iloc[0] + numpy.sum(self.bet_test[col_cote][sel_opp * sel_succes])
                self.nb_detecte[l].iloc[0] = self.nb_detecte[l].iloc[0] + numpy.sum(sel_opp)
                self.nb_tot[l].iloc[0] = self.nb_tot[l].iloc[0] + numpy.sum(len(self.y_test))
                self.succes_i[l] = [numpy.sum(sel_opp * sel_succes)]
                self.gains_i[l] = [numpy.sum(self.bet_test[col_cote][sel_opp * sel_succes])]
                self.nb_detecte_i[l] = [numpy.sum(sel_opp)]
                self.nb_tot_i[l] = [numpy.sum(len(self.y_test))]
                
            report = pandas.DataFrame()
            report['roi'] = [sum(self.gains.iloc[0]) / sum(self.nb_detecte.iloc[0])]
            report['succes'] = [sum(self.succes.iloc[0]) / sum(self.nb_detecte.iloc[0])]
            report['detection'] = [sum(self.nb_detecte.iloc[0]) / self.nb_tot[0].iloc[0]]
            report['sim'] = [i + 1]
            report.to_csv(self.config.get('output_folder','path') + 'roi.csv',sep =';',index = False)
            report_i = pandas.DataFrame()
            report_i['roi'] = [sum(self.gains_i.iloc[0]) / sum(self.nb_detecte_i.iloc[0])]
            report_i['succes'] = [sum(self.succes_i.iloc[0]) / sum(self.nb_detecte_i.iloc[0])]
            report_i['detection'] = [sum(self.nb_detecte_i.iloc[0]) / self.nb_tot_i[0].iloc[0]]
            report_i['sim'] = [i + 1]
            if i == 0:
                report_i.to_csv(self.config.get('output_folder','path') + 'roi_i.csv',sep =';',index = False)
            else:
                report_i.to_csv(self.config.get('output_folder','path') + 'roi_i.csv',sep =';',index = False,header = False,mode = 'a')
            if i == 0:
                report.to_csv(self.config.get('output_folder','path') + 'roi_append.csv',sep =';',index = False)
            else:
                report.to_csv(self.config.get('output_folder','path') + 'roi_append.csv',sep =';',index = False,header = False,mode = 'a')
