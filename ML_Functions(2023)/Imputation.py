import numpy as np
import pandas as pd
from sympy import Q

class SimpleImputer():
  def __init__(self,missing_vals="nil",strategy: str="mean",fill_value=None):
    """The function Imputes data using the transform method on the datafram which is set by fit method
    Parameters:
    missing_vals = value you want to impute (bby default np.nan/pd.NA/None/0)
    strategy = possible values [mean,median,mode,constant] Default:mean
    fill_value = value to fill if strategy set ti constant"""

    if missing_vals == "nil":
      self.missing_vals=[np.nan,None,np.NaN,np.NAN]
    else:
      self.missing_vals=[missing_vals]
    if strategy not in ["mean","median","mode","constant"]:
      raise Exception
    self.fill_value=fill_value
    self.stragety=strategy
    self.numTypes = [np.int8,np.int16,np.int32,np.int64,np.float16,np.float32,np.float64]
    
  def fit(self,df):
    if isinstance(df,pd.DataFrame):
      self.cols_to_impute = []
      self.num_cols = [x for x in df.columns if df[x].dtype in self.numTypes]
      self.str_cols = [x for x in df.columns if df[x].dtype == "object"]
    else:
      self.num_cols = [i for i,x in enumerate([*zip(*df)]) if np.array(list(x)) in self.numTypes]
      self.str_cols = [i for i,x in enumerate([*zip(*df)]) if np.array(list(x)).dtype == "object"]
  
  def transform(self,df):
    flag=0
    if not isinstance(df,pd.DataFrame): df=pd.DataFrame(df) ; flag=1
    if self.stragety=="mean":
      df = pd.DataFrame([*zip(*[df[col].fillna(df[col].mean()) for col in self.num_cols])])
    elif self.stragety=="median":
      df = pd.DataFrame([*zip(*[df[col].fillna(df[col].median()) for col in self.num_cols])])
    elif self.stragety=="mode":
      df = pd.DataFrame([*zip(*[df[col].fillna(df[col].mode()[0]) for col in self.num_cols+self.str_cols])])
    elif self.stragety=="constant":
      df = pd.DataFrame([*zip(*[df[col].fillna(self.fill_value if self.fill_value!=None else df[col].mean()) for col in self.num_cols])])
    
    if flag==1: df= np.array(df)
    return df
  
  def fit_transform(self,df):
    self.fit(df)
    return self.transform(df)

if __name__=="__main__":
  example = pd.read_csv("ML_Functions(2023)/example.csv")
  
  imputer = SimpleImputer(strategy="constant",fill_value=35)
  example = imputer.fit_transform(example)
  print(example)
