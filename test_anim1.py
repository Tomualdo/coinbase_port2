import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import time as tm
from datetime import datetime, date, time
import pandas as pd

columns = ["A1", "A2", "A3", "A4","A5", "B1", "B2", "B3", "B4", "B5", "prex"]
df = pd.DataFrame()
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111) # Create an axes. 
while True:

    now = datetime.now()
    adata = 5 * np.random.randn(1,10) + 25.
    prex = 1e-10* np.random.randn(1,1) + 1e-10
    outcomes = np.append(adata, prex)
    ind = [now]
    idf = pd.DataFrame(np.array([outcomes]), index = ind, columns = columns)
    df = df.append(idf)
    df.plot(secondary_y=['prex'], ax = ax) # Pass the axes to plot. 

    plt.draw() # Draw instead of show to update the plot in ion mode. 

    tm.sleep(0.5)