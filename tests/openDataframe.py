import pandas as pd
from datetime import date


filename = "maybeithink"
workingDir = '../data/' + "Default" + '/' + str(date.today()) + '/'
file = workingDir + filename + ".csv"

with open(file, 'rb') as f:
    data = pd.read_csv(f)

print(data)