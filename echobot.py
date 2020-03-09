import json
import requests
import time
import urllib
import io
import random
import string # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
import nltk
import wikipedia
from nltk.stem import WordNetLemmatizer

import random

TOKEN = 'telegram token'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey")
GREETING_RESPONSES = ["hi", "hey", "hiiiii", "hi there", "hello", "I am glad! You are talking to me"]
lemmer = nltk.stem.WordNetLemmatizer()
import yaml

with open(r'ai.yml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    list_convo = yaml.load(file)
#WordNet is a semantically-oriented dictionary of English included in NLTK.
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
def greeting(sentence):
    sentence=sentence.replace('+',' ')
    print("In greeting:",sentence)
    for item, doc in list_convo.items():
        for i in doc:
            if sentence.lower() in i[0].lower():
                return i[1]
def response(user_response):
    robo_response=''
    if user_response!='':
        print('coming here first');
        print(user_response)
        try:
            p = wikipedia.summary(user_response)
            #content=p.content
            sent_tokens = nltk.sent_tokenize(p)
            print('coming here');
            sent_tokens.append(user_response)
            print('coming here2');
            TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
            print('coming here3');
            tfidf = TfidfVec.fit_transform(sent_tokens)
            print('coming here4');
            vals = cosine_similarity(tfidf[-1], tfidf)
            print('coming here5');
            idx=vals.argsort()[0][-2]
            print('coming here6');
            flat = vals.flatten()
            print('coming here7');
            flat.sort()
            print('coming here8');
            req_tfidf = flat[-1]
        except:
            print("failed to get data from wikipedia");
            req_tfidf=0
    
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        
        send_message(text, chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    print('text in send:',text)
    text=text.lower()
    
    print("text in echo all:",text)
    if(text!='bye'):
        if(text=='thanks' or text=='thank you' ):
            text='ROBO: You are welcome..'
            print("ROBO: You are welcome..")
        else:
            if(greeting(text)!=None):
                print(greeting(text));
                tex1=greeting(text)
                print("ROBO: "+greeting(text))
                text=tex1
                
            else:
                print("ROBO: ",end="")
                text="ROBO: "+response(text)
                print(response(text))
               # sent_tokens.remove(user_response)
    else:
        text="ROBO: Bye! take care.."
        print("ROBO: Bye! take care..")
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()