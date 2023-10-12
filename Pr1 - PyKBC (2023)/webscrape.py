import requests
from bs4 import BeautifulSoup

def question_set(genre: str):
    """Queries the Internet and sends a dictionary of genre and 2d array of question answer as key value pair"""
    browser = requests.get("https://rjxdatascrapper.netlify.app/")
    code = BeautifulSoup(browser.content,"lxml")
    topics = code.findAll(attrs={"class":"topic"})
    print(code.prettify())
    if topics==None:
        return -1
    topicnames = [qset.find(attrs={"class":"tname"}).getText().strip() for qset in topics]
    # print(topicnames)
    questions = [[question.getText().strip().split("|") for question in topic.findAll(attrs={"class":"question"})] for topic in topics ]    
    # print(questions)
    return dict(zip(topicnames,questions))