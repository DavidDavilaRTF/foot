import pandas
import configparser
import numpy
from sklearn import linear_model,neighbors,svm,preprocessing,tree,ensemble

class ia_prod:
    def __init__(self,db,db_prod,db_team_prod,db_cote_prod,col_y,col_cote_dom,col_cote_nulle,col_cote_ext,type_model,config):
        self.col_y = col_y
        self.col_cote_dom = col_cote_dom
        self.col_cote_ext = col_cote_ext
        self.col_cote_nulle = col_cote_nulle
        self.y = db[[self.col_y]]
        self.x = db.drop(col_y,axis = 1)
        self.x_prod = db_prod
        self.col_x = self.x.columns
        self.x_prod = self.x_prod[self.col_x]
        self.bet_prod = db_cote_prod
        self.config = config
        self.type_model = type_model
        self.db_team_prod = db_team_prod
        self.res = db_prod[['res']]

    def standardization(self):
        x_temp = self.x.append(self.x_prod)
        scaler = preprocessing.StandardScaler()
        scaler.fit(x_temp)
        self.x = scaler.transform(self.x)
        self.x = pandas.DataFrame(self.x)
        self.x.columns = self.col_x
        self.x_prod = scaler.transform(self.x_prod)
        self.x_prod = pandas.DataFrame(self.x_prod)
        self.x_prod.columns = self.col_x
    
    def prediction(self):
        nb_label = numpy.array(self.y[self.col_y].unique())
        nb_label = numpy.sort(nb_label)
        self.standardization()
        y_sans_modifier = self.y.copy()
        report = pandas.DataFrame()
        for l in nb_label:
            sel_label = numpy.array(y_sans_modifier[self.col_y] == l)
            sel_no_label = numpy.array(y_sans_modifier[self.col_y] != l)
            self.y[self.col_y][sel_label] = 1
            self.y[self.col_y][sel_no_label] = 0

            if self.type_model == 'logit':
                model = linear_model.LogisticRegression()
            elif self.type_model == 'tree':
                model = tree.DecisionTreeClassifier()
            elif self.type_model == 'rf':
                model = ensemble.RandomForestClassifier()
            elif self.type_model == 'knn':
                model = neighbors.KNeighborsClassifier()
            model.fit(self.x,self.y)
            pr = numpy.array(model.predict_proba(self.x_prod)[:,1])

            if l == -1:
                col_cote = self.col_cote_ext
            elif l == 0:
                col_cote = self.col_cote_nulle
            elif l == 1:
                col_cote = self.col_cote_dom

            opp = pandas.DataFrame(pr * numpy.array(self.bet_prod[col_cote]))
            sel_opp = numpy.array(opp[opp.columns[0]] > 1)
            if sum(sel_opp) > 0:
                report_l = pandas.DataFrame()
                report_l = self.db_team_prod[sel_opp]
                report_l['res'] = numpy.array(self.res[sel_opp])
                report_l['bet'] = l
                report_l['confiance'] = numpy.array(pandas.DataFrame(pr)[sel_opp])
                report_l['odds'] = numpy.array(self.bet_prod[col_cote][sel_opp])
                report_l['roi'] = numpy.array(report_l['confiance']) * numpy.array(report_l['odds']) - 1
                report_l.index = range(len(report_l))
                report = report.append(report_l)
                report.index = range(len(report))
        report.to_csv(self.config.get('output_folder','path') + 'opp.csv',index = False,sep = ';')
