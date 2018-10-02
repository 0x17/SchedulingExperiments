import warnings

import autosklearn.metrics
import autosklearn.regression
import pandas as pd
from sklearn.model_selection import train_test_split
import sklearn.metrics

import numpy as np

def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true))

df = pd.read_csv('datamerged_regress_j30.csv', header=0, index_col=0)

xs_all = df[df.columns[:-1]]
ys_all = df['optimalObjective']

xs, xs_test, ys, ys_test = train_test_split(xs_all, ys_all, train_size=0.9, random_state=1)

print('Training on '+str(len(xs))+' samples. Validating on '+str(len(xs_test))+' samples.')

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

cls = autosklearn.regression.AutoSklearnRegressor(time_left_for_this_task=900, per_run_time_limit=360, ensemble_size=1)
cls.fit(xs, ys, xs_test, ys_test, feat_type=['numerical']*8, metric=autosklearn.metrics.mean_absolute_error)
print(cls.show_models())
#print(cls.cv_results_)
print(cls.sprint_statistics())
#predictions = cls.predict(xs_test)