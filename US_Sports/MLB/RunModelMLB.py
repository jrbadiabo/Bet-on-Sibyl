# coding: utf-8

# In[1]:

import csv
import sqlite3 as lite
import sys

from matplotlib import pyplot as plt
from pandas import *
from sklearn.model_selection import train_test_split, cross_val_predict, cross_val_score
from sklearn import linear_model, metrics, svm
from sklearn import preprocessing
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import shuffle


# get_ipython().magic(u'matplotlib inline')


# -----------------------------CLASS 'MAKE_PREDICTIONS'-------------------------------

def plot_confusion_matrix(cm, title='Confusion matrix'):
    plt.title(title)
    fig = plt.figure()
    # create a grid of subplots
    ax = fig.add_subplot(111)
    # declare a var that shows the confusion matrix
    cax = ax.matshow(cm)
    # Create a colorbar for a ScalarMappable instance, mappable
    fig.colorbar(cax)
    plt.ylabel('True value')
    plt.xlabel('Predicted value')
    plt.savefig('confusion_matrix.png')
    plt.show()

    # ----------------------------------------------------------------------------------------------------------------------------------------


def plot_response(subset_sizes, train_errs, test_errs):
    plt.plot(subset_sizes, train_errs, lw=2)
    plt.plot(subset_sizes, test_errs, lw=2)
    plt.legend(['Training accuracy', 'Test accuracy'])
    plt.xscale('log')
    plt.xlabel('Dataset size')
    plt.ylabel('Accuracy')
    plt.title('Model response to dataset size')
    plt.show()


def normalize_features(X):
    minmax_scale = preprocessing.MinMaxScaler().fit(X)
    X = minmax_scale.transform(X)
    return X


def standardize_features(X):
    std_scale = preprocessing.StandardScaler().fit(X)
    X = std_scale.transform(X)
    return X


def add_id_column_to_csv(tableau_input_filename):
    df = read_csv(tableau_input_filename)
    df.index.name = 'ID'
    df.to_csv(tableau_input_filename, mode='w+', index=True)


class MLBMakePredictions(object):
    # Applies ml techniques to the mlb scraped data and uses the 
    # resulting model to make predictions on unplayed games 
    # (NB: unplayed game = mlb_db_name = mlb_team_data_x.db, for ex. the database of the CURRENT SEASON, 
    # the season you want to make prediction)

    from ScrapeMLBTeamStats import AcquireTeamStats
    from ScrapeMLBGameStats import AcquireGameStats
    from PrepareForMLTechMLB import PrepareForML

    def __init__(self, current_season, feature_file, mlb_db_name):
        self.data = np.load(feature_file)
        self.tableau_input_filename = "mlb_tableau_input" + str(current_season) + '.csv'
        self.current_season = current_season
        self.X = self.data['X']
        self.y = self.data['y']
        self.mlb_db_name = mlb_db_name

    def __call__(self):
        print "Scraping MLB current season data for update...\n"
        self.acquire_current_season_data(self.current_season)
        # Train again on our data from 'features.npz' because for 'learning curves'
        # we performed the training process in the CV function
        print "Algorithm training..."
        self.train_logistic_regression()
        print "OK\n"

        print "Making predictions..."
        self.make_tableau_file(self.game_data_filename, self.datetime_filename)
        print "OK\n"
        add_id_column_to_csv(self.tableau_input_filename)

    # -----------------------ACQUIRE CURRENT SEASON DATA---------------------------
    def acquire_current_season_data(self, current_season):
        # Acquires all data structures needed to make predictions on current season 

        team_data_filename = 'mlb_team_stats_' + str(current_season) + '.csv'
        game_data_filename = 'mlb_game_stats_' + str(current_season) + '.csv'
        datetime_filename = 'mlb_datetime_' + str(current_season) + '.csv'
        db_filename = 'mlb_team_data_' + str(current_season) + '.db'
        feature_filename = 'mlb_' + str(current_season) + '_features.npz'
        # if you want to filter,
        # uncomment and make changes to the corresponding section in the 'AcquireGameStats' class

        # Scrape data for the current season
        print "Scraping Team Stats..."
        mlb_teamdata = self.AcquireTeamStats(current_season, current_season, current_season, team_data_filename)
        mlb_teamdata()
        print "OK\n"

        print "Scraping Game Stats..."
        mlb_gamedata = self.AcquireGameStats(current_season, current_season, current_season, game_data_filename,
                                             datetime_filename)
        mlb_gamedata()
        print "OK\n"

        print "Preprocessing updated data for Machine Learning..."
        # Prepare for ML predictions
        pml = self.PrepareForML(game_data_filename, db_filename)
        pml.process_raw_data(team_data_filename)
        pml(feature_filename)
        print "OK\n"

        self.datetime_filename = datetime_filename
        self.game_data_filename = game_data_filename

    # -------------------------------------------CREATING CSV FILE FOR TABLEAU----------------------------------

    def make_tableau_file(self, game_data_filename, datetime_filename):
        # Produces a csv file containing predicted and actual game results for the current season
        # Tableau uses the contents of the file to produce visualization

        with open(self.tableau_input_filename, 'wb') as writefile:
            tableau_write = csv.writer(writefile)
            tableau_write.writerow(
                ['Visitor_Team', 'V_Team_PTS', 'Home_Team', 'H_Team_PTS', 'True_Result', 'Predicted_Result',
                 'Confidence', 'Date'])

            with open(game_data_filename, 'rb') as readfile, open(datetime_filename, 'rb') as readfile2:
                scorereader = csv.reader(readfile)
                scores = [row for row in scorereader]
                scores = scores[1::]
                daysreader = csv.reader(readfile2)
                days = [day for day in daysreader]
                if (len(scores) != len(days)):
                    print("File lengths do not match")
                else:
                    for i in range(len(days)):
                        tableau_content = scores[i][1::]
                        tableau_date = days[i]
                        # Append True_Result
                        try:
                            if int(tableau_content[3]) > int(tableau_content[1]):
                                tableau_content.append(1)
                            else:
                                tableau_content.append(0)
                        except:
                            pass
                        # Append 'Predicted_Result' and 'Confidence'
                        prediction_results = self.make_predictions(tableau_content[0], tableau_content[2])
                        tableau_content += list(prediction_results)
                        tableau_content += tableau_date

                        tableau_write.writerow(tableau_content)
                        # -----------------------------------------------------------------------------------------------------------------------------------------

                        # -----------------------------ADD INDEX COLUMN TO CSV FOR TABLEAU ANALYSIS-----

                        # To run after the 'make_tableau_file' function so as to add 'ID' column to the
                        #  'tableau_input' file and so indexing each game...
                        # and thus facilitate analysis of each game in Tableau

    # E.G. THIS IS THE FILE TO TAKE FOR BETTING STRATEGIES IN TABLEAU!!!!

    # ----------------------------------------ALGORITHMS-------------------------------------------------------------------------------------
    # Each of the algorithm has a separation between 'instanciating
    # + training to the data' and only 'intanciating' (required for k-fold CV)

    # Logistic Regression
    def train_logistic_regression(self, scale_data=False):
        # IF YOU PASS 'scale_data' to True
        # DO NOT FORGET TO DO THE SAME IN 'make_predictions' to also normalize test data (current_season features)
        # Preprocessing step: False by default
        # Scaling the feature vector applying normalization 'Min-Max scaling' technique
        # If you want to use standardization use 'standardize_features' function
        # Hint: Better use normalization for SVM
        # (http://www.csie.ntu.edu.tw/~cjlin/papers/guide/guide.pdf) or try both and
        # compare the results with cross validation
        if scale_data != False:
            self.X = standardize_features(self.X)
        else:
            pass
        X, y = shuffle(self.X, self.y)
        self.logreg = linear_model.LogisticRegression()
        self.logreg.fit(X, y)

    def instantiate_logistic_regression(self):
        # Only instantiate logistic regression model without fitting any data
        # Needed in the 'model_evaluation' function
        self.logreg2 = linear_model.LogisticRegression()
        pass

    # Radial Basis Function kernel SVM
    def train_rbf_svm(self, scale_data=True):
        # IF YOU PASS 'scale_data' to True DO NOT FORGET TO DO THE SAME IN 'make_predictions' 
        # to also normalize test data (current_season features)        
        # Preprocessing step: True by default(only for SVM as it is always recommended)
        # Scaling the feature vector applying normalization 'Min-Max scaling' technique
        # If you want to use standardization use 'standardize_features' function
        # Hint: Better use normalization for SVM
        # (http://www.csie.ntu.edu.tw/~cjlin/papers/guide/guide.pdf) or try both and
        # compare the results with cross validation
        if scale_data != False:
            self.X = normalize_features(self.X)
        else:
            pass
        X, y = shuffle(self.X, self.y)
        self.clf = svm.SVC(probability=True, random_state=None)
        self.clf.fit(X, y)

    def instantiate_rbf_svm(self):
        self.clf2 = svm.SVC(probability=True, random_state=None)

        pass

    def train_adaboost(self):
        X, y = shuffle(self.X, self.y)
        self.dbt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=100)
        self.dbt.fix(X, y)

    def instantiate_adaboost(self):
        self.dbt2 = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=100)
        pass

    # --------------------------------------------------------------------------------------------------------------------------------------

    # -----------------------MAKE PREDICTIONS (implemented in the 'make_tableau_file function)-----------------

    def make_predictions(self, team1, team2, scale_data=False):
        # Using prediction model, returns 1 if the model thinks team2 will beat team1, 0 otherwise
        # Advise: Respect the order:
        # V_Team for team1, H_Team for team2 for consistency with the PrepareForML class techniques

        query = 'SELECT * FROM Team_Stats WHERE Team = ?'

        con = lite.connect(self.mlb_db_name)
        with con:
            cur = con.cursor()
            cur.execute(query, (team1,))
            feature1 = list(cur.fetchone()[2::])
            cur.execute(query, (team2,))
            feature2 = list(cur.fetchone()[2::])
            feature = np.array(feature2).reshape(1, -1) - np.array(feature1).reshape(1, -1)

            if scale_data != False:
                feature = normalize_features(feature)

            else:
                pass

            # Make prediction 
            # TO CHANGE ACCORDING THE ALGORITHM YOU WANT TO USE, 
            # available classifiers: logreg, clf, dbt (change 2X)
            prediction_output = self.logreg.predict(feature)  # Predict class labels for samples in X
            prediction_probability = max(
                self.logreg.predict_proba(feature)[0])  # Returns the probability of "prediction_output"

            return prediction_output[0], prediction_probability

    # -------------------------------------PARAMETRIC--------------------------------------------

    def cval_score(self):
        # change 'logreg' to 'clf' if you want to perform it on SVM (dbt also available)
        scores = cross_val_score(self.logreg, self.X, self.y, cv=10)
        print scores.mean(), scores.std()

    # Used in for learning curves and model evaluation
    def train_test_split(self):
        self.trX, self.teX, self.trY, self.teY = train_test_split(self.X, self.y, test_size=0.30, random_state=None)
        pass

    # ----------------------------------CROSS VALIDATION AND MODEL EVALUATION-----------------------------

    # The below function takes a model,
    # a pre-split dataset(train/test X and Y arrays (Nb: use train_test_split function to do so)),
    # a scoring function as input and iterates through the dataset training
    # on n exponentially spaced subsets and returns the learning curves
    # e.g. score_func = metrics.accuracy_score
    def data_size_response(self, model, score_func, prob=True, n_subsets=10):

        # creating 2 empty arrays for train
        train_errs, test_errs = [], []
        # defining a var that take the value of "n_subsets" and creates "n_subsets" with corresponding size
        # "linspace returns num evenly spaced samples, calculated over the interval [start, stop]
        # shape[0] of an array Y of dimensions (n,m) merely means "n", number of rows
        subset_sizes = np.exp(np.linspace(3, np.log(self.trX.shape[0]), n_subsets)).astype(int)

        # looping over the subset_sizes
        for m in subset_sizes:
            # for each subset we fit the model on trX, trY
            model.fit(self.trX[:m], self.trY[:m])
            # if prob is 'True', we defining var 'train_err' & 'test_err'
            # which are scores of Y (true Y) and 'predict_proba' made on X (predict Y)
            # respectively for the train and test set
            if prob:
                train_err = score_func(self.trY[:m], model.predict_proba(self.trX[:m]))
                test_err = score_func(self.teY, model.predict_proba(self.teX))
            # if prob is 'True', we defining var 'train_err' & 'test_err'
            # which are scores of Y (true Y) and 'predict' made on X (predict Y)
            # respectively for the train and test set
            else:
                train_err = score_func(self.trY[:m], model.predict(self.trX[:m]))
                test_err = score_func(self.teY, model.predict(self.teX))
            # printing the results for the m subset
            print "training error(accuracy): %.3f test error(accuracy): %.3f subset size: %.3f" % (
                train_err, test_err, m)
            # appending the m results to the arrays 'train_errs' & 'test_errs'
            train_errs.append(train_err)
            test_errs.append(test_err)

        # returning the number of subsets and the arrays
        return subset_sizes, train_errs, test_errs

    # Plotting function for visualizing the above response, e.g. the train error and the test error

    # Instruction to execute the above functions
    # model = it is the model we use e.g LogisticRegression()
    # score_func = it is the score function we use e.g. cval_score()
    # We declare a variable response = data_size_response(model, trX, teX, trY, teY, score_func, prob=True, n_subsets=?)
    # We plot the response: plot_response(*response)

    def model_evaluation(self):

        # Do not forget to replace the classifier by the one you want to evaluate
        # Classifiers: logreg2, clf2, dbt2
        self.train_test_split()
        y_pred = self.logreg2.fit(self.trX, self.trY).predict(self.teX)
        # predictions are in columns and actual values in rows
        cm = metrics.confusion_matrix(self.teY, y_pred)
        # nb: The support is the number of occurrences of each class in y_true (e.g. what really happened)
        print metrics.classification_report(self.teY, y_pred)
        print "matthews correlation coefficent: %.2f" % (metrics.matthews_corrcoef(self.teY, y_pred))
        accuracy = float(cm[0][0] + cm[1][1]) / cm.sum()
        print "accuracy: %.2f" % (accuracy)
        away_accuracy = float(cm[0][0]) / (cm[0][0] + cm[0][1])
        print "away_accuracy: %.2f" % (away_accuracy)
        home_accuracy = float(cm[1][1]) / (cm[1][1] + cm[1][0])
        print "home_accuracy: %.2f" % (home_accuracy)
        plot_confusion_matrix(cm, title='Confusion matrix')


if __name__ == '__main__':
    x = MLBMakePredictions(2016, "mlb_1980_2014_features.npz", "mlb_team_data_2016.db")
    x()
