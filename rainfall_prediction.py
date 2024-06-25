# -*- coding: utf-8 -*-
"""Rainfall_prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1q8kKmQZiFMnkgybX_6fgVW7hNMjLpKtA
"""

from google.colab import drive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
import pandas as pd

# Mount Google Drive
drive.mount('/content/drive')

# Authenticate and create the PyDrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

# Specify the file ID from the provided Google Sheets link
source_id = '14DuS314o3m7CWHRPPiRTMz5moOBhMP_R3ECxhj2Y_MU'

# Search to make sure the shortcut doesn't exist already
flist = drive.ListFile({'q': f'shortcutDetails.targetId="{source_id}" and trashed=false'}).GetList()

if not flist:
    # Create shortcut if file doesn't exist
    shortcut = drive.CreateFile({
        'mimeType': 'application/vnd.google-apps.shortcut',
        'shortcutDetails': {
            'targetId': source_id
        },
        'title': 'My Spreadsheet Shortcut'
    })
    shortcut.Upload()
    print('Shortcut created successfully.')
else:
    print('Shortcut already exists.')

# Export and download the file as .xlsx
file = drive.CreateFile({'id': source_id})
file.GetContentFile('transformed_rainfall_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Read the .xlsx file using Pandas
df_original = pd.read_excel('transformed_rainfall_data.xlsx')
print(df_original.head())

# Assuming your dataframe is named 'df'
df = df_original[~df_original.index.isin([0, 1])]

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Convert the date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')

# Extracting day of the year as a feature
df['DayOfYear'] = df['Date'].dt.dayofyear

# Select features and target
features = ['DayOfYear']
targets = ['Vavuniya', 'Anuradhapura', 'Maha Illuppallama']

# Calculate and plot ACF and PACF for each target column
for target in targets:
    # Calculate and plot ACF
    fig, ax = plt.subplots()
    plot_acf(df[target].dropna(), ax=ax, lags=30)  # Adjust lags as needed
    plt.title(f"Autocorrelation of {target}")
    plt.show()

    # Calculate and plot PACF
    fig, ax = plt.subplots()
    plot_pacf(df[target].dropna(), ax=ax, lags=30)  # Adjust lags as needed
    plt.title(f"Partial Autocorrelation of {target}")
    plt.show()

# Lag features (previous day's value)
for target in targets:
  df[f'{target}_lag1'] = df[target].shift(1)

# Calculate rolling statistics
window_size = 7  # You can experiment with different window sizes

for target in targets:
    df[f'{target}_rolling_mean_{window_size}'] = df[target].rolling(window=window_size).mean()
    df[f'{target}_rolling_std_{window_size}'] = df[target].rolling(window=window_size).std()
    df[f'{target}_rolling_median_{window_size}'] = df[target].rolling(window=window_size).median()

# After feature engineering
df.dropna(inplace=True)  # Drop rows with any NaN values

# Plot the rolling mean and standard deviation
for target in targets:
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df[target], label='Original')
    plt.plot(df['Date'], df[f'{target}_rolling_mean_{window_size}'], label=f'Rolling Mean ({window_size} days)')
    plt.plot(df['Date'], df[f'{target}_rolling_std_{window_size}'], label=f'Rolling Std ({window_size} days)')
    plt.plot(df['Date'], df[f'{target}_rolling_median_{window_size}'], label=f'Rolling Median ({window_size} days)')
    plt.title(f'Rolling Statistics for {target}')
    plt.legend()
    plt.show()

df.head()

df.columns

from sklearn.model_selection import train_test_split

# Specify the features and include the relevant lag and rolling statistics columns
features = [
    'DayOfYear',
    'Vavuniya_lag1', 'Anuradhapura_lag1', 'Maha Illuppallama_lag1',
    'Vavuniya_rolling_mean_7', 'Vavuniya_rolling_std_7', 'Vavuniya_rolling_median_7',
    'Anuradhapura_rolling_mean_7', 'Anuradhapura_rolling_std_7', 'Anuradhapura_rolling_median_7',
    'Maha Illuppallama_rolling_mean_7', 'Maha Illuppallama_rolling_std_7', 'Maha Illuppallama_rolling_median_7'
]

# Select the features from the DataFrame
X = df[features]
y_vavuniya = df['Vavuniya']
y_anuradhapura = df['Anuradhapura']
y_maha = df['Maha Illuppallama']



X_train, X_test, y_train_v, y_test_v = train_test_split(X, y_vavuniya, test_size=0.2, random_state=42)
X_train, X_test, y_train_a, y_test_a = train_test_split(X, y_anuradhapura, test_size=0.2, random_state=42)
X_train, X_test, y_train_m, y_test_m = train_test_split(X, y_maha, test_size=0.2, random_state=42)

"""## SARIMA

## Decision Trees
"""

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Train the Decision Tree Regressor for each target
def train_and_evaluate_model(X_train, X_test, y_train, y_test, target_name):
    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model performance for {target_name}:")
    print(f"Mean Absolute Error: {mae}")
    print(f"Mean Squared Error: {mse}")
    print(f"R-squared: {r2}")
    print()

    return model

# Train and evaluate models for each target
model_vavuniya = train_and_evaluate_model(X_train, X_test, y_train_v, y_test_v, 'Vavuniya')
model_anuradhapura = train_and_evaluate_model(X_train, X_test, y_train_a, y_test_a, 'Anuradhapura')
model_maha = train_and_evaluate_model(X_train, X_test, y_train_m, y_test_m, 'Maha Illuppallama')

import joblib
joblib.dump(model_vavuniya, 'model_vavuniya.joblib')
joblib.dump(model_anuradhapura, 'model_anuradhapura.joblib')
joblib.dump(model_maha, 'model_maha.joblib')

