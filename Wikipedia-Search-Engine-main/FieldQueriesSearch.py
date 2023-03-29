from operator import indexOf
import pickle
import os
import json
import string
index={}
with open('Json_Index.json','rb') as file:
    data = json.load(file)

tfidfMap=data[1]
querry = input("Enter the querry: ")
#Assuming that fields are separated by commas;
array=querry.split(",")
dict1={}
for word in array:
    arr=word.split(":")
    dict1[arr[0]]=arr[1]
index=data[0]
query_tfidf={}

for key,text in dict1.items():
    word1=text.split(" ")
    for word in word1:
        if word in index:
            temp = index[str(word)]
            tfidf=""
            i=len(temp)-1
            while(temp[i]!=':'):
                tfidf+=temp[i]
                i-=1
            tfidf=tfidf[::-1]
            i-=1
            fields=""
            while(temp[i]!=':'):
                fields+=temp[i]
                i-=1
            fields=fields[::-1]
            fields=fields.split()
            for k in range(0,len(fields[0])-1):
                if(key==fields[0][k]):
                    if(fields[0][k+1]!=0):
                        query_tfidf[word]=float(tfidf)


cosine_scores={}        
rankings={}
for doc in tfidfMap.keys():
     dict1=tfidfMap[doc]
     score=0
     for word in query_tfidf.keys():
         if word in dict1.keys():
             score+=dict1[word]*query_tfidf[word]
     rankings[doc]=score

rankingList=[]
for key in rankings.keys():
    rankingList.append([rankings[key],key])

rankingList.sort(reverse=True)

docIdtoTitle=data[2]
i=0
for i in range(0,10):
    print(docIdtoTitle[rankingList[i][1]]+"::"+str(rankingList[i][1]))