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
import pandas_datareader.data as web

plt.style.use("fivethirtyeight")

# data = pd.read_csv('OMG Network Historical Data - Investing.com.csv')
# data = pd.read_csv('OMG Network Historical Data - Investing.com.csv')
# data[['Date','Price','Open','High','Low','Vol.','Change %']] = data[['Date','Price','Open','High','Low','Vol.','Change %']].values[::-1]

data = web.DataReader('OMG-EUR',data_source='yahoo',start='2012-01-01',end='2020-11-30')

# plt.figure(figsize=(12.5,4.5))
# plt.plot(data['Price'],label=['minute'])
# plt.title(' close')
# plt.xlabel('Time')
# plt.ylabel('close price (€)')
# plt.legend(loc='upper left')
# plt.show()

#create data frame with only close
data1 = data.filter(['Close'])
#convert to numy array
data2 = data1.values
#get numer of rows to train model
training_data_len = math.ceil(len(data2) * .5)


#scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data2)

#create training dataset
#create scaled training dataset
train_data = scaled_data[0:training_data_len,:]
#split data to x tarin and y train data set
x_train = []
y_train = []

begin = 60

for i in range(begin,len(train_data)):
    x_train.append(train_data[i-begin:i,0])
    y_train.append(train_data[i,0])
    if i<=begin+1:
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
model.add(keras.layers.LSTM(begin-10,return_sequences=True,input_shape=(x_train.shape[1],1)))
model.add(keras.layers.LSTM(begin-10,return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#compile the model
model.compile(optimizer='adam',loss='mean_squared_error')

#Train the model
model.fit(x_train,y_train,batch_size=1,epochs=1)

#create testing dataset
#create new array coining scaled values from index <LAST> to <FUTURE>
test_data = scaled_data[training_data_len - begin:,:]
#create data set x,y sets
x_test = []
y_test = data2[training_data_len:,:]
for i in range(begin, len(test_data)):
    x_test.append(test_data[i-begin:i,0])

#convert data to numpy array
x_test = np.array(x_test)
#reshape the data
x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

#Get the model predicted the price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#get the root mean squared error
rmse=np.sqrt(np.mean(((predictions- y_test)**2)))
print("root mean squared error:",rmse)

#plot the data
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions
#visualize
plt.figure(figsize=(16,8))
plt.title('model')
plt.xlabel('Date',fontsize=18)
plt.ylabel('close')
plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])
plt.legend(['Train','Val','Predictions'],loc='upper right')
plt.show()