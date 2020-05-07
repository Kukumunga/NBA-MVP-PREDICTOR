# -*- coding: utf-8 -*-
"""MVP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gdgaODaT8yKi6-4ma6UI7ka0iSUakcg7

# Preprocessing The Data

## Imports
"""

# imports
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

# READ CSV using pandas
filepath = '/content/'
season_stats = pd.read_csv(filepath+'seasons_stats.csv').drop('Unnamed: 0',axis=1)
ss_18_20 = pd.read_csv(filepath+'season_stats_2018-2020.csv').drop('Unnamed: 0',axis=1)
vote = pd.read_csv(filepath+'voting.csv').drop(['AGE','Unnamed: 0'],axis=1)
team_performance = pd.read_csv(filepath+'team_performance.csv')

"""## Creating Dataset"""

SS = season_stats[season_stats['YEAR'] >= 1980]

# Remove unwanted rows and columns #DO NOT RE-RUN 
#SS = SS.drop(columns=["Unnamed: 0"])
SS = SS[SS.YEAR.notnull()]
#remove special characters in the Players col
SS['PLAYER'] = SS['PLAYER'].replace({'\*':''}, regex=True)

# add missing data to the set
SS = pd.concat([SS,ss_18_20],ignore_index=True)

# merge season stats and voting
full_stats = pd.merge(SS, vote,  how='left', left_on=['YEAR','PLAYER','TEAM'],
                      right_on = ['YEAR','PLAYER','TEAM'])

full_stats = full_stats.fillna(0)

full_stats

##### PLAYERS TO DELETE ######
##### ONLY RUN ONCE DURING RUNTIME #####
# DeAndre Liggins 2014 
# index 16839
# had the all time highest win share because he only played one game and highest PER
# Naz Mitrou-Long
# index 19348
# had the all time highest win share because he only played one game and highest PER
pos = [16839,19348]
full_stats.drop(full_stats.index[pos], inplace=True)

"""#MVP Possible Models

## SVM

In this section I used an SVM model to narrow down as small of a list of candidates for each MVP voting year.
"""

import pandas as pd 
import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.preprocessing import scale
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import seaborn as sns
from scipy import stats

data = full_stats

"""I want to only be able to find how the top five players in voting are. Three points weren't a thing until 89' and only became the meta in the modern NBA. May have to look at only a subset of the data beacause we are looking to predict future voting and that relates more to modern NBA values."""

# drop_svm = ['POS','AGE','TEAM','GS','3PAr','FTr','ORB%','DRB%','TRB%'
# ,'AST%','STL%','BLK%','TOV%','USG%','OBPM','DBPM','BPM','VORP','FGA',
# '3P','3PA','2P','2PA','2P%','FT','FTA','First','PW','PM','PF']

drop_final = ['POS','AGE','TEAM','GS','3PAr','FTr','ORB%','DRB%','TRB%'
,'AST%','STL%','BLK%','TOV%','USG%','OBPM','DBPM','BPM','VORP','FGA',
'3P','3PA','2P','2PA','2P%','FT','FTA','First','PW','PM','PF','ORB','DRB','FG',
'TOV','MP','WS']

data = data.drop(drop_final,axis=1)

data = data[data['YEAR'] > 2003]
print(data)

# make train and test sets for first set of predictions
ranking = range(1,3) 
train = data[data['YEAR'] <= 2015]
#print(train.iloc[:,2:-5])
x_train = scale(train.iloc[:,2:-1])
y_train = train['RANK'].apply(lambda x: -1 if (x not in ranking) else 1)
test = data[data['YEAR'] > 2015]
x_test = scale(test.iloc[:,2:-1])
y_test = test['RANK'].apply(lambda x: -1 if (x not in ranking) else 1)

print("x_train:",np.shape(x_train))
print("y_train:",np.shape(y_train))
print("x_test:",np.shape(x_test))
print("y_test:",np.shape(y_test))

# Checking the distribution of the labels
sns.distplot(y_test)

clf = SVC(kernel='linear')
clf.fit(x_train,y_train)
y_pred = clf.predict(x_test)
print(accuracy_score(y_test,y_pred))

"""### Checking Results"""

d = {'player': test['PLAYER'], 'year': test['YEAR'], 'RANK': (test['RANK']), 'pred': y_pred}
df = pd.DataFrame(data=d)

df[df.pred == 1]

# create a new df so we can see if can predict the actual MVP in this list
narrowed = test
narrowed['PRED'] = y_pred
narrowed = narrowed[narrowed['PRED'] == 1]

narrowed

"""## Selecting MVP"""

# XGBoost
import xgboost
from sklearn.metrics import explained_variance_score

drop_final = ['POS','AGE','TEAM','GS','3PAr','FTr','ORB%','DRB%','TRB%'
,'AST%','STL%','BLK%','TOV%','USG%','OBPM','DBPM','BPM','VORP','FGA',
'3P','3PA','2P','2PA','2P%','FT','FTA','First','PW','PM','PF','ORB','DRB','FG',
'TOV','MP','WS']

data = full_stats[full_stats['RANK'] != 0]

data = data.drop(drop_final,axis=1)

data = data[data['YEAR'] > 2005]
data = data[data['RANK'] <= 5]

data

# make train and test sets 
train = data[data['YEAR'] <= 2016]
#print(train.iloc[:,2:-5])
x_train = scale(train.iloc[:,2:-1])
y_train = train['RANK'].apply(lambda x: 0 if (x != 1) else 1)
test = data[data['YEAR'] > 2016]
x_test = scale(test.iloc[:,2:-1])
y_test = test['RANK'].apply(lambda x: 0 if (x != 1) else 1)

# Checking the distribution of the labels
sns.distplot(y_test)

"""### XGB"""

# Let's try XGboost algorithm to see if we can get better results
xgb = xgboost.XGBRegressor(n_estimators=100, learning_rate=0.01, gamma=0, subsample=0.75,
                           colsample_bytree=1, max_depth=6)

xgb.fit(x_train,y_train)

predictions = xgb.predict(x_test)
t_predict = xgb.predict(x_train)
print(explained_variance_score(predictions,y_test))

# candidates
#drop_narrowed = ['ORB',	'DRB','FG','TOV','MP','WS']
#candidates = narrowed.drop(drop_narrowed,axis=1)
candidates = narrowed
cand_scaled = scale(candidates.iloc[:,2:-2])

print("x_train:",np.shape(x_train))
print("y_train:",np.shape(y_train))
print("x_test:",np.shape(x_test))
print("y_test:",np.shape(y_test))
print("candidates:",np.shape(cand_scaled))

n_pred = xgb.predict(cand_scaled)

candidates['X_PRED'] = n_pred

candidates.sort_values(['YEAR', 'X_PRED'], ascending=[True, False])

"""#### Comments

After many tries tuning the parameters, this was a great result. The only incorrect prediction was in 2019, but that year the MVP was highly debated and talked about. Being that the prediction was close, this could mean that this could be a useful model

### Linear Regression
"""

import numpy as np
from sklearn.linear_model import LinearRegression

reg = LinearRegression().fit(x_train,y_train)
reg.score(x_train,y_train)

reg.coef_

reg.intercept_

candidates['L_PRED'] = reg.predict(cand_scaled)

candidates.sort_values(['YEAR', 'L_PRED'], ascending=[True, False])

"""#### Comments

This model made all the correct predictions, though the 2016 vote should more in favour of Steph Curry that year due to him being the first unanimous MVP

### Random Forrest
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression

regr = RandomForestRegressor(random_state=0,n_estimators=100)
regr.fit(x_train,y_train)
print(regr.feature_importances_)

candidates['R_PRED'] = regr.predict(cand_scaled)

candidates.sort_values(['YEAR', 'R_PRED'], ascending=[True, False])

"""#### Comments

With tunning the parameters I was not able to get results that I liked with this set of predictions. Specifically it strongly favours Harden over Giannis in 2019.

# MVP for 2020 season

I need to first scale the 2020 season to make the numbers seem as though everyone has played a full season.
"""

data = full_stats[full_stats['YEAR'] == 2020].drop('RANK',axis=1)

"""First let's get rid of players who haven't played much this season. If we scale those players we will find they'll end up with great stats due to them potientially having insane PER for playing a game or two"""

data = data[data['G'] > 13]

"""Since all the features are season totals we can just find the per game averges and mulitply it by 82 (total games there should be in a season).

Instead we'll use 72 games due to that fact that most players don't play all 82 games
"""

total_games = 72
fields = ['MP','FG', 'ORB', 'DRB', 'TRB', 'AST', 'STL',
       'BLK', 'TOV', 'PTS']

for i in fields:
  data[i] = (data[i]//data['G'])*total_games
data['G'] = total_games

data = data.drop(drop_final,axis=1)

"""Now we can narrow down our candidate pool of players"""

# create a new df so we can see if can predict the actual MVP in this list
narrowed = data
narrowed['PRED'] = clf.predict(scale(data.iloc[:,2:]))
narrowed = narrowed[narrowed['PRED'] == 1]

narrowed

"""## MVP"""

#MVP = narrowed.drop(drop_narrowed,axis=1)
MVP = narrowed
mvp_scaled = scale(MVP.iloc[:,2:-1])

MVP['X_PRED'] = xgb.predict(mvp_scaled)
MVP['F_PRED'] = reg.predict(mvp_scaled)

MVP['X_PRED'] = xgb.predict(mvp_scaled)

MVP.sort_values(['YEAR', 'F_PRED'], ascending=[True, False])

MVP.sort_values(['YEAR', 'X_PRED'], ascending=[True, False])

"""## Comments

I decided to go for to test both XGB and LR, since both fit well as potienal models. 

Running both results we see that LR performed much closer to what the actaul discussion was this season. 

Looking at the results for LR I'm very pleased seeing that the top two predictions are Giannis and LeBron. The talk this season has been between the two of them and is the topic of many NBA debate shows.
"""