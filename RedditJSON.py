# https://www.reddit.com/r/news/comments/84v9y9/britain_is_now_threatening_to_seize_russian/.json

import json
from operator import itemgetter
from pprint import pprint

fileName = "AllPostings.json"

json_data=open(fileName)
data = json.load(json_data)
json_data.close()

totalNumOfPostings = len(data["data"]["children"])
allPostingsList = list()

for i in range (totalNumOfPostings):
    title = data["data"]["children"][i]["data"]["title"]
    score = data["data"]["children"][i]["data"]["score"]
    subreddit = data["data"]["children"][i]["data"]["subreddit_name_prefixed"]
    subscribers = data["data"]["children"][i]["data"]["subreddit_subscribers"]
    allPostingsList.append((title, score, subreddit, subscribers))

allPostingsList = sorted(allPostingsList,key=itemgetter(1), reverse=True)

for i in allPostingsList:
    print(i[2] + " | " + str(i[3]) + " subscribers")
    print(str(i[1]) + "pts | " + i[0])
    print()

print("----------------------------------\n")

fileName = "BritainIsThreateningToSeize.json"

# with open(fileName, 'r') as fin:
#     print fin.read()

json_data=open(fileName)
data = json.load(json_data)
#pprint(data)
json_data.close()

url = data[0]["data"]["children"][0]["data"]["url"]
title = data[0]["data"]["children"][0]["data"]["title"]
totalParentComments = len(data[1]["data"]["children"])
postScore = data[0]["data"]["children"][0]["data"]["score"]
parentCommentsList = list()

print("URL: " + url)
print("Title: " + title)
print("Score: " + str(postScore) + " points")
print()



for i in range (totalParentComments-1):
    comment = data[1]["data"]["children"][i]["data"]["body"]
    score = data[1]["data"]["children"][i]["data"]["score"]
    parentCommentsList.append((comment, score))

parentCommentsList = sorted(parentCommentsList,key=itemgetter(1), reverse=True)

for i in parentCommentsList:
    print(str(i[1]) + "pts - " + i[0])