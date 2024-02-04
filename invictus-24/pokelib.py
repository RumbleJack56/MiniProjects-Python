import requests
from fastai.learner import load_learner
import os
import solution
import matplotlib.pyplot as plt
import cv2
class pokemon():
    def __init__(self,name: str):
        self.name=name.lower()
        raw=requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
        a = raw.content
        a = eval(a.decode("utf-8").replace(':false',':"false"').replace(':true',':"true"').replace(':null',':"null"'))
        del a['moves']
        self.types = [t["type"]["name"] for t in a['types']]
        self.stats = dict([[t['stat']['name'],t['base_stat']] for t in a["stats"]])
        self.height = a["height"]
        self.weight = a["weight"]
        self.id = a["id"]

    def __repr__(self): return self.name,self.id,self.types,self.stats,self.height,self.weight
    def __str__(self): return f"( Name: {self.name} , Id: {self.id} , Types : {self.types} , Stats : {self.stats} , Height : {self.height} , Weight : {self.weight} )"

def findPromimentPokemon(inputImage : solution.Segment_Image or solution.Crypt_Image):
    os.chdir(f"E:\College\Journey\AIMS\Invictus-24")
    model = load_learner(fname="PokemonClassifier.pkl")
    cv2.imwrite('testPokemon.jpg',inputImage.img)
    sol = model.predict('testPokemon.jpg')
    return pokemon(sol[0].lower())