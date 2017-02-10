# coding: utf-8

# In[ ]:
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

# ----------------------CLASS 'MAKE_PREDICTIONS'---------------------


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
    assert isinstance(X, object)
    return X


def standardize_features(X):
    std_scale = preprocessing.StandardScaler().fit(X)
    X = std_scale.transform(X)
    return X


class FootballTop5MakePredictions(object):
    # Apply ML techniques to the top 5 football leagues scrapped data and use
    # of the resulting model to make predictions on unplayed games
    # NB: unplayed games are in the football_top5_db_name_FOR_THE_CURRENT_SEASON
    #  (ex 'football_top5_db_name_2017') => season on which you want to
    # make predictions

    from ScrapeFootballTop5TeamStats import AcquireFootballTop5TeamStats
    from ScrapeFootballTop5GameStats import AcquireFootballTop5GameStats
    from PrepareForMLTechFootballTop5 import PrepareForML

    def __init__(self, current_season, ps_feature_filename, football_top5_db_name):
        """

        :type ps_feature_filename: object
        """
        self.data = np.load(ps_feature_filename)
        self.current_season = current_season
        self.tableau_output_filename = "football_top5_tableau_output_" + str(current_season) + '.csv'
        self.X = self.data['X']
        self.y = self.data['y']
        self.football_top5_db_name = football_top5_db_name

    def __call__(self):

        self.acquire_current_season_data(self.current_season)
        # Train once again our data from 'football_top5_features.npz' so as to show the learning curves
        # Perform the training process in the CV function
        self.train_logistic_regression()
        self.make_tableau_file(self.game_data_filename, self.datetime_filename,
                               self.league_filename)
        self.add_id_column_to_csv(self.tableau_output_filename)

    # ----------------------------ACQUIRE CURRENT SEASON DATA ------------------------------------------

    def acquire_current_season_data(self, current_season):
        # Acquires all data structures needed to make predictions on current season matchups

        team_data_filename = 'football_top5_team_stats_' + str(current_season) + '_' + str(current_season) + '.csv'
        game_data_filename = 'football_top5_game_stats_' + str(current_season) + '_' + str(current_season) + '.csv'
        datetime_filename = 'date_football_top5_game_stats_' + str(current_season) + '_' + str(current_season) + '.csv'
        league_filename = 'football_top5_matchup_league_' + str(current_season) + '_' + str(current_season) + '.csv'
        football_top5_db_filename = 'football_top5_team_data_' + str(current_season) + '.db'
        cs_feature_filename = 'football_top5_features_' + str(current_season) + '.npz'
        # If you want to filter,
        # uncomment and make changes to the corresponding section in the 'AcquireGameStats' class

        # Scrape top 5 leagues data for the current season
        football_top5_team_data = self.AcquireFootballTop5TeamStats(current_season, current_season)
        football_top5_team_data()
        football_top5_game_data = self.AcquireFootballTop5GameStats(current_season, current_season)
        football_top5_game_data()

        # Prepare for ML predictions 
        pml = self.PrepareForML(game_data_filename, football_top5_db_filename, team_data_filename)
        pml(cs_feature_filename)

        # Set class variables that we will use later on

        self.league_filename = league_filename
        self.game_data_filename = game_data_filename
        self.datetime_filename = datetime_filename

    # ---------------------------------------------------------------------------------------------------
    # ----------------------------------------CREATE CSV OUTPUT FOR TABLEAU -----------------------------

    def make_tableau_file(self, game_data_filename, datetime_filename, league_filename):
        # Produces a csv file containing predicted and actual
        # game results for the current season that can see in Tableau

        with open(self.tableau_output_filename, 'wb') as writefile:
            tableau_write = csv.writer(writefile)
            tableau_write.writerow(
                ['Visitor_Team', 'V_Team_PTS', 'Home_Team', 'H_Team_PTS', 'True_Result', 'Predicted_Result',
                 'Confidence', 'Date', 'League_T'])

            with open(game_data_filename, 'rb') as readfile, open(datetime_filename, 'rb') as readfile2, open(
                    league_filename, 'rb') as readfile3:
                scorereader = csv.reader(readfile)
                scores = [row for row in scorereader]
                scores = scores[1::]
                daysreader = csv.reader(readfile2)
                days = [day for day in daysreader]
                leaguesreader = csv.reader(readfile3)
                leagues = [league for league in leaguesreader]

                if (len(scores) != len(days)):
                    print("File lengths for scores/days do not match")
                elif (len(scores) != len(leagues)):
                    print("File lengths for scores/leagues do not match")
                else:
                    for i in range(len(days)):
                        tableau_content = scores[i][1::]
                        tableau_date = days[i]
                        tableau_league = leagues[i]

                        # Append True_Result
                        try:
                            if int(tableau_content[3]) > int(tableau_content[1]):
                                tableau_content.append(1)
                            elif int(tableau_content[3]) == int(tableau_content[1]):
                                tableau_content.append(0)
                            else:
                                tableau_content.append(2)
                        except:
                            pass
                        # Append Predicted_Result and Confidence
                        prediction_results = self.make_predictions(tableau_content[0], tableau_content[2])
                        tableau_content += list(prediction_results)
                        tableau_content += tableau_date
                        tableau_content += tableau_league

                        tableau_write.writerow(tableau_content)

                        # ---------------------------- ADD INDEX COLUMN TO CSV FOR TABLEAU ANALYSIS -----------------

                        # NB: To run AFTER the 'make_tableau_file' function so as to add an 'ID'
                        # column to the tableau_output file and thus indexing
                        # each game. => Ease the analysis of each game in Tableau

    @staticmethod
    def add_id_column_to_csv(tableau_output_filename):
        df = read_csv(tableau_output_filename)
        df.index.name = "ID"
        df.to_csv(tableau_output_filename, mode='w+', index=True)

    # -------------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------ALGORITHMS-----------------------------------------------------------

    # NB!!!! Each of the algorithms has a separation between
    # 'instanciating + training to the data' and only 'instanciating'
    # which required for k-fold CV

    # --------Logistic Regression----------
    def train_logistic_regression(self, scale_data=False):
        # IF you pass 'scale_data' = True, DO NOT FORGET
        # to do the same in 'make_predictions' function to also normalize test
        # test data (current season). Preprocessing step: False by default.
        # Scaling the feature vector applying normalization
        # 'Min-Max scaling' technique. If you want to use standardization use 'standardize_features' function instead
        # Hint: Better use normalization for SVM 

        if scale_data != False:
            self.X = standardize_features(self.X)
        else:
            pass
        X, y = shuffle(self.X, self.y)
        self.logreg = linear_model.LogisticRegression(multi_class='ovr')
        self.logreg.fit(X, y)

    def instantiate_logistic_regression(self):
        # Only instantiate a linear model without fitting any data
        # Needed in the model evaluation function
        self.logreg2 = linear_model.LogisticRegression(multi_class='ovr')
        pass

    # ---------Radial Basis Function kernel SVM------------
    def train_rbf_svm(self, scale_data=False):
        # Same hint => See hint for 'train_logistic_regression'

        if scale_data != False:
            self.X = standardize_features(self.X)
        else:
            pass
        X, y = shuffle(self.X, self.y)
        self.clf = svm.SVC(probability=True, random_state=None)
        self.clf.fit(X, y)

    def instantiate_rbf_svm(self):
        self.clf2 = svm.SVC(probability=True, random_state=None)
        pass

    # --------Ensemble Methods: AdaBoostClassifier------------

    def train_adaboost(self):
        X, y = shuffle(self.X, self.y)
        self.dbt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=100)
        self.dbt.fit(X, y)

    def instantiate_adaboost(self):
        self.dbt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=100)
        pass

    # --------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    # ------------------------MAKE_PREDICTION Function (implemented in 'make_tableau_file' function------

    def make_predictions(self, team1, team2, scale_data=False):
        # Using the chosen classifier,
        # return 1 if the the model thinks Home_Team (team2)will beat the Visitor_Team (team1)
        # NB: Respect the order for the implementation in the 'make_tableau_file' function. Visitor_team = team1 
        # Home_team = team2 => for consistency with the PrepareForML class techniques

        query = 'SELECT * FROM Team_Stats WHERE Team = ?'

        con = lite.connect(self.football_top5_db_name)
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

            # Make prediction part: to change according the classifier you want to use
            # available classifiers: logreg, clf, dbt (change 2X when you choose a classifier)
            prediction_output = self.logreg.predict(feature)  # Predict class labels for samples in X
            prediction_probability = max(
                self.logreg.predict_proba(feature)[0])  # Returns the probabily of the prediction

            return prediction_output[0], prediction_probability  # Why 'prediction_output[0]... Cannot remember...

            # -----------------------------------------------PARAMETRIC---------------------------------------

    def cval_score(self):
        # change 'logreg' to 'clf' if you want to perform it on SVM (dbt also available)
        scores = cross_val_score(self.logreg, self.X, self.y, cv=10)
        print scores.mean(), scores.std()

    # Used in for learning curves and model evaluation
    def train_test_split(self):
        self.trX, self.teX, self.trY, self.teY = train_test_split(self.X, self.y, test_size=0.30, random_state=None)
        pass

    # -------------------------------------------------------------------------------------------------------
    # ----------------------------------------CROSS VALIDATION AND MODEL EVALUATION -------------------------

    # The below function takes a model and make a evaluation:
    # a pre-split dataset(train/test X and y array (nb: use train_test_split
    # function to do so)),
    # a scoring function as input and iterates through the dataset training on n exponentially spaced subsets and
    # returns the learning curves e.g. score_func = metrics.accuracy_score

    def data_size_response(self, model, score_func, prob=True, n_subsets=10):
        # creating 2 empty arrays for train
        train_errs, test_errs = [], []
        # defining a var that take the value of n_subsets and creates n_subsets with corresponding size.
        # "linspace returns num evenly spaced samples,
        # calculated over the interval [start, stop]. shape[0] of an array y of dimension (n,p) merely means
        # 'n', => n of rows
        subset_sizes = np.exp(np.linspace(3, np.log(self.trX.shape[0]), n_subsets)).astype(int)

        # looping over the subset sizes 
        for m in subset_sizes:

            #  for each subset we fit the model on trX, trY
            model.fit(self.trX[:m], self.trY[:m])

            # if prob is 'True',
            # we define var'train_err' & 'test_err' which are scores of Y (true Y) and 'predict_proba' made on X
            # (predict Y). respectively for the train and test set
            if prob:
                train_err = score_func(self.trY[:m], model.predict_proba(self.trX[:m]))  # m is the size of the subset
                test_err = score_func(self.teY, model.predict_proba(self.teX))

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

    # Plotting function for visualizing the above response, e.g. the train error and test error

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
