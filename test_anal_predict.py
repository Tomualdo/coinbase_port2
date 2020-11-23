from typing import Sequence
import pandas as pd
import numpy as np
import json
from datetime import datetime
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from tensorflow.python.keras.layers.core import Dense

plt.style.use("fivethirtyeight")

data = {
    "OMG": [
        {
            "minute": "15.10.2020 21:19",
            "open": "9817.77",
            "high": "9820",
            "low": "9817.77",
            "close": "9820"
        },
        {
            "minute": "15.10.2020 21:39",
            "open": "9838.5",
            "high": "9847.17",
            "low": "9834.99",
            "close": "9844.38"
        },
        {
            "minute": "15.10.2020 21:20",
            "open": "9819.96",
            "high": "9820",
            "low": "9818.75",
            "close": "9820"
        }
    ],
    "BTC": [
        {
            "minute": "15.10.2020 21:39",
            "open": "9838.5",
            "high": "9847.17",
            "low": "9834.99",
            "close": "9844.38"
        },
        {
            "minute": "15.10.2020 21:42",
            "open": "9847.05",
            "high": "9847.05",
            "low": "9843.14",
            "close": "9845.78"
        }]
}
# print(pd.json_normalize(data,'OMG'))
# print(pd.json_normalize(data,'BTC'))

f = open("data.json", "r")
a = json.load(f)
data = pd.json_normalize(a,'BTC')
# print(data)

#convert columns to correct dataTypes
data[['open','close','high','low']] = data[['open','close','high','low']].apply(pd.to_numeric)
# data[['minute']] = data[['minute']].apply(pd.to_datetime) 

#convert date column to correct dataTypes with formating
data[['minute']] = pd.to_datetime(data['minute'],format='%d.%m.%Y %H:%M')

# convert all columns of DataFrame
# df = df.apply(pd.to_numeric) # convert all columns of DataFrame

# convert just columns "a" and "b"
# df[["a", "b"]] = df[["a", "b"]].apply(pd.to_numeric)

# print(data.dtypes)
# print(data)

plt.figure(figsize=(12.5,4.5))
# plt.plot(data['minute'],data['close']) #use if time is without interuption
plt.plot(data['close'],label='time')
plt.title('close')
plt.xlabel('minute')
plt.ylabel('close price')
plt.legend(loc='upper left')
# plt.gcf().autofmt_xdate()
# plt.show()

#create data frame with only close
data1 = data.filter(['close'])
#convert to numy array
data2 = data1.values
#get numer of rows to train model
training_data_len = math.ceil(len(data2) * .8)
# print(training_data_len)

#scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data2)

#create training dataset
#create scaled training dataset
train_data = scaled_data[0:training_data_len,:]
#split data to x tarin and y train data set
x_train = []
y_train = []

for i in range(60,len(train_data)):
    x_train.append(train_data[i-60:i,0])
    y_train.append(train_data[i,0])
    if i<=61:
        print(x_train)
        print(y_train)
        print()

#convert x_train and y_train to numpy array
x_train,y_train = np.array(x_train),np.array(y_train)

#reshape the data
x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
print(x_train.shape)

#buld LSTM model
model = keras.Sequential()
model.add(keras.layers.LSTM(50,return_sequences=True,input_shape=(x_train.shape[1],1)))
model.add(keras.layers.LSTM(50,return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#compile the model
model.compile(optimizer='adam',loss='mean_squared_error')

#Train the model
model.fit(x_train,y_train,batch_size=1,epochs=1)

#create testing dataset
#create new array coining scaled values from index <LAST> to <FUTURE>
test_data = scaled_data[training_data_len - 60:,:]
#create data set x,y sets
x_test = []
y_test = data2[training_data_len:,:]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i,0])

#convert data to numpy array
x_test = np.array(x_test)
#reshape the data
x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

#Get the model predicted the price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#get the root mean squared error
rmse = np.sqrt(np.mean(predictions - y_test)**2)

#plot the data
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions
#visualize
plt.figure(figsize=(16,8))
plt.title('model')
plt.xlabel('Date',fontsize=18)
plt.ylabel('close')
plt.plot(train['close'])
plt.plot(valid[['close','Predictions']])
plt.legend(['Train','Val','Predictions'],loc='lower right')
plt.show()