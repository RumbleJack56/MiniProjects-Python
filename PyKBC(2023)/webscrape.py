import requests
from bs4 import BeautifulSoup

def question_set(genre: str=""):
    """Queries the Internet and sends a dictionary of genre and 2d array of question answer as key value pair"""
    
    browser = requests.get("https://rjxdatascrapper.netlify.app/")
    code = BeautifulSoup(browser.content,"lxml")

    topics = code.findAll(attrs={"class":"topic"})
    if topics==None:
        return -1
    
    
    topicnames = [topic.find(attrs={"class":"tname"}).getText().strip() for topic in topics]

    questions = [[question.getText().strip().split("|") for question in topic.findAll(attrs={"class":"question"})] for topic in topics ]    

    if genre != "":
    
        if genre not in topicnames:
            return -1
    
        return dict([str,questions[topicnames.index(str)]])
    
    return dict(zip(topicnames,questions))


def main():
    print(question_set())

if __name__ == "__main__":
    main()