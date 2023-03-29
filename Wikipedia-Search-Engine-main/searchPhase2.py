from curses.ascii import isalpha, isdigit
from hashlib import new
from operator import indexOf
import pickle
import os
import ast
import re
import json
import timeit
index={}

def BinarySearch(word,l,r) -> float:
    while(l<=r):
        mid=int(l+(r-l)/2)
        with open('OutputFolder/Index'+str(mid)+'.json','rb') as file:
            data = json.load(file)

        if(word in data):
            tfidf=""
            temp = data[word]
            i=len(temp)-1
            while(i>=0 and temp[i]!=':'):
                tfidf+=temp[i]
                i-=1
            tfidf=tfidf[::-1]
            return tfidf
        elif(len(data)>0 and word>str(next(iter(data)))):
            l=mid+1
        else:
            r=mid-1

    return -1


querry = input("Enter the querry: ")
array = querry.split(' ')

query_tfidf={}
for word in array:
    tfidf= BinarySearch(word,1,909)
    query_tfidf[word]=tfidf
    print(tfidf)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False



cosine_scores={}        
rankings={}
for i in range(1,9114):
    with open('OutputFolder/Index'+str(i)+'.json','rb') as file:
        data=file.read().decode()
        data=data.split(",")
        for i in range(0,len(data)):
            data[i]=data[i].split(":")
        for doc in data:
            if(len(doc)==3):
                score=0
                num=doc[0]
                i=0
                newString=doc[1]
                newString=newString[2:]
                for word in query_tfidf.keys():
                        num1=""
                        for k in range(0,len(query_tfidf[word])):
                            if(query_tfidf[word][k]=='\n'): break
                            num1+=query_tfidf[word][k]
                            k+=1
                        num2=""
                        for k in range(0,len(doc[2])):
                            if(doc[2][k]=='"' or doc[2][k]=='\n'): break
                            num2+=doc[2][k]
                            k+=1
                        #print(str(num1)+"::"+str(num2))
                        if isfloat(num1) and isfloat(num2):
                            score+=float(num2)*float(num1)
                rankings[num]=score

#print(rankings)
rankingList=[]
for key in rankings.keys():
    rankingList.append([rankings[key],key])
rankingList.sort(reverse=True)
print(rankingList[0:10])


ans=[]
for j in range(0,10):
    #print(type(rankingList[j][1]))
    b=False
    for i in range(9114,9534):
        with open('OutputFolder/Index'+str(i)+'.json','rb') as file:
            data=file.read().decode()
            data=data.split(",")
            for doc in data:
                doc=str(doc)
                doc=doc.split(":")
                if(len(doc)>1 and doc[0]==rankingList[j][1]):
                    ans.append(doc[1])
                    b=True

print(ans[0:100])
