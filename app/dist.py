import pandas as pd
import numpy as np
import sklearn

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MaxAbsScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD

def sake_distance(db, sakeid):
    n_res = 10
    # print("selected sake id:", sakeid, "number of results:", n_res)
    df = pd.read_sql('sake', con=db.engine, index_col='index')
    # None -> np.nan, important for categorical imputation, scikit-learn won't take None as missing values
    df = df.fillna(value=np.nan)
    # Fix the missing Polish_Ratio by using the most frequent values in each Sake category
    sake_PR_mode_bytype = df.loc[df['Polish_Ratio'].notnull(),['Polish_Ratio','Type_cat']]\
                            .groupby(['Type_cat']).agg(lambda x: x.value_counts().index[0]).values
    # impute the missing values to polish ratio
    for i, pr in enumerate(sake_PR_mode_bytype, 1):
        df.loc[(df['Polish_Ratio'].isnull()) & (df['Type_cat']==i), 'Polish_Ratio'] = \
        [pr] * len(df.loc[(df['Polish_Ratio'].isnull()) & (df['Type_cat']==i), 'Polish_Ratio'])

    # Pipeline Setup
    # numeric_features = ['SMV', 'Acidity']
    numeric_features = ['SMV', 'Acidity', 'ABV', 'Polish_Ratio']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='median'))])

    categorical_features = ['Type_cat', 'Varietal']
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(missing_values=np.nan, strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore')),
        ('svd', TruncatedSVD(n_components=100))])

    features = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)])
    est = Pipeline([
        ('features', features),
        ('scaling', MaxAbsScaler()),
        ('estimator', NearestNeighbors(n_neighbors=(n_res+1), algorithm= 'brute', metric= 'cosine'))
    ])

    est.fit(df)

    sake_transformscaled = est['scaling'].transform(features.transform(df[df.index==int(sakeid)]))
    # print(sake_transformscaled)
    dists, indices = est['estimator'].kneighbors(sake_transformscaled)
    # print(df.loc[int(sakeid),:])
    # print(type(sakeid))
    # print("distance:", dists[0])
    # print("indices:", df.index[indices[0]])
    idx = np.where(df.index[indices[0]] == int(sakeid))
    # print('sakeid locates at index:', idx[0])

    # add the sakeid item as the first item of the return list
    if idx: # if sakeid is in the recommendation list
        return [0] + np.delete(dists[0], idx[0]).tolist()[:n_res], \
        [int(sakeid)] + np.delete(df.index[indices[0]], idx[0]).tolist()[:n_res]

    return [0] + dists[0].tolist()[:n_res], [int(sakeid)] + df.index[indices[0]].tolist()[:n_res];
