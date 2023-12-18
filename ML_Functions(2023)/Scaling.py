from matplotlib import scale
import numpy as np
import pandas as pd

class StandardScaler():
  def __init__(self,with_mean=True,scaleFactor="std"):
    """
    with_mean: centers the data around the mean (True/False)
    scaleFactor: scale factor for the data ("std","max",None)
    """
    if scaleFactor not in ["std","max",None,"None"]: raise Exception
    self.with_mean = with_mean
    self.scaleFactor = scaleFactor
    self.numTypes = [np.int8,np.int16,np.int32,np.int64,np.float16,np.float32,np.float64]
    
  def fit(self,df:pd.DataFrame):
    d2 = df.copy()
    self.num_cols = [x for x in d2.columns if df[x].dtype in self.numTypes]
  def transform(self,df:pd.DataFrame):
    d2 = df.copy()
    for cols in self.num_cols:
      if self.with_mean==True: d2[cols] = [x - d2[cols].mean() for x in list(d2[cols])]
      
      if self.scaleFactor=="max":maxval=d2[cols].max();d2[cols] = [x/maxval for x in list(d2[cols])]
      elif self.scaleFactor=="std":maxval=d2[cols].std();d2[cols] = [x/maxval for x in list(d2[cols])]
    return d2

  def fit_transform(self,df:pd.DataFrame):
    self.fit(df)
    return self.transform(df)

if __name__ == "__main__":
  scaler = StandardScaler()
  example = pd.read_csv("ML_Functions(2023)/example.csv")
  print(example)
  print(scaler.fit_transform(example))