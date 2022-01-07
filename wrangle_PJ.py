import env
import acquire_PJ
import numpy as np

from sklearn.model_selection import train_test_split
# rmse to check baseline and model
from sklearn.metrics import mean_squared_error

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# removes outliers via quartile 
def remove_outliers(df, k, col_list):
    ''' remove outliers from a list of columns in a dataframe 
        and return that dataframe
    '''

    for col in col_list:

        q1, q3 = df[col].quantile([.25, .75])  # get quartiles
        
        iqr = q3 - q1   # calculate interquartile range
        
        upper_bound = q3 + k * iqr   # get upper bound
        lower_bound = q1 - k * iqr   # get lower bound

        # return dataframe without outliers
        
        df = df[(df[col] > lower_bound) & (df[col] < upper_bound)]
        
    return df


# Splitting my data
def split(df, target_var):
    
    # split df into train_validate (80%) and test (20%)
    train_validate, test = train_test_split(df, test_size=.2, random_state=123)
    
    # split train_validate into train(70% of 80% = 56%) and validate (30% of 80% = 24%)
    train, validate = train_test_split(train_validate, test_size=.3, random_state=123)

    # create X_train by dropping the target variable 
    X_train = train.drop(columns=[target_var])
    # create y_train by keeping only the target variable.
    y_train = train[[target_var]]

    # create X_validate by dropping the target variable 
    X_validate = validate.drop(columns=[target_var])
    # create y_validate by keeping only the target variable.
    y_validate = validate[[target_var]]

    # create X_test by dropping the target variable 
    X_test = test.drop(columns=[target_var])
    # create y_test by keeping only the target variable.
    y_test = test[[target_var]]

    partitions = [train, X_train, y_train, validate, X_validate, y_validate, test, X_test, y_test]
    return partitions

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# Changes 'year_built' name to 'age'
def yearbuilt_years(df):
    df.yearbuilt =  df.yearbuilt.astype(int)
    year = date.today().year
    df['age'] = year - df.yearbuilt
    # dropping the 'yearbuilt' column now that i have the age
    df = df.drop(columns=['yearbuilt'])
    return df

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# Create a function that will remove rows and columns that have missing values past a certain threshold.
def handle_missing_values(df, p_row = 0.84, p_col = 0.84):
    ''' function which takes in a dataframe, required notnull proportions of non-null rows and columns.
    drop the columns and rows columns based on theshold:'''
    
    #drop columns with nulls
    threshold = int(p_col * len(df.index)) # Require that many non-NA values.
    df.dropna(axis = 1, thresh = threshold, inplace = True)
    
    #drop rows with nulls
    threshold = int(p_row * len(df.columns)) # Require that many non-NA values.
    df.dropna(axis = 0, thresh = threshold, inplace = True)
    
    
    return df
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# State DF and state cols for example : ['age', 'taxes', 'area'] (set as alist of strings for the columns to remove)
# Enter data fram and list of columns that you want to drop
def drop_columns(df, drop_col):
    df = df.drop(columns=drop_col)
    return df

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# Cleans the data
def prep_zillow(df):
    
    df = handle_missing_values(df)

    # Create a list of columns to drop.
    columns_to_drop = ['transactiondate','assessmentyear','id','Unnamed: 0','parcelid','calculatedbathnbr'
                   ,'finishedsquarefeet12','fullbathcnt','propertycountylandusecode','propertylandusetypeid',
                   'rawcensustractandblock','regionidcity','regionidcounty','regionidzip',
                   'structuretaxvaluedollarcnt','censustractandblock','propertylandusedesc', 'roomcnt']

    df = drop_columns(df, columns_to_drop)

    for col in df.columns:
    if df[col].isna().sum() > 0:
        df[col] = df[col].fillna(value = df[col].mean())

    df = df.rename(columns = {'fips':'county', 'calculatedfinishedsquarefeet' : 'area', 'bathroomcnt' : 'bathrooms',
                         'bedroomcnt' : 'bedrooms', 'poolcnt' : 'pools', 'garagecarcnt' : 'garages',
                          'taxvaluedollarcnt': 'tax_value'})

    df = yearbuilt_years(df)

    # Cleaning the data
    # Creating counties
    df['LA_County']= df['county'] == 6037
    df['Orange_County']= df['county'] == 6059
    df['Ventura_County']= df['county'] == 6111


    df['LA_County'] = df['LA_County'].replace(False, 0)
    df['LA_County'] = df['LA_County'].replace(True, 1)

    df['Orange_County'] = df['Orange_County'].replace(False, 0)
    df['Orange_County'] = df['Orange_County'].replace(True, 1)

    df['Ventura_County'] = df['Ventura_County'].replace(False, 0)
    df['Ventura_County'] = df['Ventura_County'].replace(True, 1)

    df = df[df.bedrooms != 0]
    df = df[df.bathrooms != 0]

    # Later Lets look at pools and garages!
    # Create new features here

    df['acres']= df.lotsizesquarefeet/43560


    # ratio of bathrooms to bedrooms
    df['bed_bath_ratio'] = df.bedrooms / df.bathrooms

    # bin ages
    df['age_bins'] = pd.cut(df.age, 
                               bins = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
                               labels = [0, .066, .133, .20, .266, .333, .40, .466, .533, 
                                     .60, .666, .733, .8, .866, .933])

    #  bin acres
    df['acres_bin'] = pd.cut(df.acres, bins = [0, .10, .15, .25, .5, 1, 5, 10, 20, 50, 200], 
                    labels = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9])

    df = df.astype({'acres_bin': float, 'age_bins': float})

    col_list = ['bedrooms', 'bathrooms', 'area', 'tax_value',
            'lotsizesquarefeet', 'taxamount', 'age', 'acres',
           'bed_bath_ratio', 'landtaxvaluedollarcnt']
    k = 1.5
    
    df = remove_outliers(df, k, col_list)

    return df
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
# Cleans and splits the data
def wrangle_zillow(df):
    
    df = prep_zillow(df)

    partitions = split(df, target_var = 'logerror')
    
    return partitions


# Enter train without main target and scales data
def scale_zillow(X_train):

    scaler = MinMaxScaler(copy=True)
    x_train_scaled = scaler.fit_transform(X_train)

    x_train_scaled = pd.DataFrame(x_train_scaled, columns = X_train.columns.to_list())

    return scaled_df
    
# use scaled and y train to output the RFE
def rfe_features_zillow(scaled, y_train):
    # initialize the ML algorithm
    lm = LinearRegression()

    # create the rfe object, indicating the ML object (lm) and the number of features I want to end up with. 
    rfe = RFE(lm, 4)

    # fit the data using RFE
    rfe.fit(scaled,y_train)  

    # get the mask of the columns selected
    feature_mask = rfe.support_

    # get list of the column names. 
    rfe_feature = x_train_scaled.iloc[:,feature_mask].columns.tolist()

    return rfe_feature

def basline(y_train):
    y_train = pd.DataFrame(y_train)

    y_train['baseline_mean'] = y_train['logerror'].mean()
    #y_train['baseline_med'] = y_train['logerror'].median()
    rmse_train = mean_squared_error(y_train.logerror, y_train.baseline_mean)**(1/2)
    
    return y_train, print("RMSE using Mean \n Train / In-Sample", round(rmse_train, 5))

#def rmse_mean(y_train):
 #   rmse_train = mean_squared_error(y_train.logerror, y_train.baseline_mean)**(1/2)
 #   return print("RMSE using Mean \n Train / In-Sample", round(rmse_train, 5))