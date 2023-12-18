import numpy as np
import pandas as pd


class OrdinalEncoder():
  def __init__(self,string_only=True,handle_unknown: str="error",unknown_value=None):
    self.handle_unknown = handle_unknown
    self.unknown_value = unknown_value
    self.string_only = string_only
    
  def fit(self, df:pd.DataFrame):
    if self.string_only:
      self.colstoencode = [x for x in df.columns if df[x].dtype == "object"]
    else:
      self.colstoencode = df.columns
    self.columnlist = []
    for col in self.colstoencode:
      a = list(df[col] )
      b = []
      for x in a:
        if x not in b: b.append(x)
      self.columnlist.append([x[::-1] for x in enumerate(b)])

  def transform(self,df:pd.DataFrame):
    d2 = df.copy()
    for collist , col in zip(self.columnlist, self.colstoencode):
      collist = [*zip(*collist)]
      d2[col].replace(to_replace=collist[0],value=collist[1],inplace=True)
    return d2

  def fit_transform(self,df:pd.DataFrame):
    self.fit(df)
    return self.transform(df)

  def inverse_transform(self,df:pd.DataFrame):
    d2 = df.copy()
    for collist , col in zip(self.columnlist, self.colstoencode):
      collist = [*zip(*collist)]
      d2[col].replace(to_replace=collist[1],value=collist[0],inplace=True)
    return d2

class OneHotEncoder():
  def __init__(self,handle_unknown: str="error",max_cardinality: int=15):
    self.handle_unkown=handle_unknown
    self.max_cardinality = max_cardinality
    
  def fit(self,df:pd.DataFrame):
    self.colstoencode = [x for x in df.columns if df[x].dtype == "object" and df[x].nunique()<=self.max_cardinality]
    
    self.columnlist = []
    for col in self.colstoencode:
      a = list(df[col])
      b = []
      for x in a:
        if x not in b: b.append(x)
      self.columnlist.append(b)

  def transform(self,df:pd.DataFrame):
    d2 =df.copy()
    for collist , cols in zip(self.columnlist,self.colstoencode):
      L = list(d2[cols])
      for listitem in collist:
        d2[listitem+"_"+cols] = [1 if listitem==x else 0 for x in L]
      d2 = d2.drop(cols,axis=1)
    return d2

  def fit_transform(self,df:pd.DataFrame):
    self.fit(df)
    return self.transform(df)


if __name__ == "__main__":
  encoder = OrdinalEncoder()
  example = pd.read_csv("ML_Functions(2023)/example.csv")
  encoder.fit(example)
  
  ex2 = encoder.transform(example)
  print(ex2)
  print()
  print(encoder.inverse_transform(ex2))


  encoder2 = OneHotEncoder()
  encoder2.fit(example)
  
  print(encoder2.transform(example))