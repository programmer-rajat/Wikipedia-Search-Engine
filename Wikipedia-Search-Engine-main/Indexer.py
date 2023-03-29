from curses.ascii import isdigit
from tokenize import PseudoExtras
import xml.sax
from collections import OrderedDict
from collections import defaultdict
import timeit
import re
import sys
import nltk
import json
import string
import math
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
import pickle
from itertools import islice

Stopwords = set(stopwords.words('english'))
DocId_to_titleMap={}
numDoc=1
PostingList={}
uniqueWords=set()
infoBoxcnt={}
refrencescnt={}
cateogriescnt={}
titlecnt={}
bodycnt={}
MyIndex={}
processedInfoBox=set()
processedrefrences=set()
processedcategories=set()
processedbody=set()
processedTitle=set()
wordToDocId = defaultdict(list)
stemmedWordsDict={}
initialWords=0
FinalWords=0
tfidfMap={}
docIDtoTitle={}

def tokenise(data):
    tok=[]
    tok=re.findall(r'[a-z]+',data)
    return tok

porter = PorterStemmer()
def preProcess(text):
   global initialWords
   text = "".join([char for char in text if char not in string.punctuation])
   tokens = tokenise(text)
   initialWords+=len(tokens)
   for word in tokens:
        if(len(word)>15):
            tokens.remove(word)
        if(len(word)<2):
            tokens.remove(word)

   filtered_tokens = [word for word in tokens if word not in Stopwords]
   for word in tokens:
        if word not in Stopwords:
            filtered_tokens.append(word)

   stemmedWord=set()
   for word in filtered_tokens:
        if word in stemmedWordsDict:
            stemmedWord.add(stemmedWordsDict[word])
        else:
            stemword=porter.stem(word)
            stemmedWord.add(stemword)
            stemmedWordsDict.setdefault(word,stemword)

   return stemmedWord

class Handler(xml.sax.ContentHandler):
    def __init__(self):
        self.idCount=0
        self.titleCount=0
        self.textCount=0
        self.isText=False
        self.isTitle=False


    def startElement(self, name, attrs):
        if(name=='title'):
            self.titleCount+=1
            self.isTitle=True
        if(name=='text'):
            self.textCount+=1
            self.isText=True
        if(name=='id'):
            self.idCount+=1

    def endElement(self, name):
        if(name=='text'):
            self.isText=False
        if(name=='title'):
            self.isTitle=False

    def characters(self, content):
        if(self.isTitle):
            global numDoc
            global processedTitle
            global wordToDocId
            global docIDtoTitle
            processedTit=preProcess(content)
            for word in processedTit:
                processedTitle.add(word)
                wordToDocId[word].append(numDoc)
            numDoc+=1
            docIDtoTitle[numDoc]=content

        if(self.isText):
            infoBox=str(re.findall(r'(?=\{Infobox)\{([^{}]|()*\})',content))
            refrences=re.findall(r'== ?references ?==\n(.*?)\n\n',content)
            categories = re.findall(r'\[\[Category:([^\]]*\b)', content)
            body=re.findall(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]',content)

            global processedInfoBox
            global processedrefrences
            global processedcategories
            global processedbody
            global tfidfMap
            
            processedInfo=preProcess(infoBox)
            processedref=preProcess(refrences)
            processedcats=preProcess(categories)
            processedb=preProcess(body)
            

            for word in processedInfo:
                processedInfoBox.add(word)
                wordToDocId[word].append(numDoc)
                if numDoc in tfidfMap.keys():
                    if word in tfidfMap[numDoc].keys():
                        tfidfMap[numDoc][word]+=1
                    else:
                        tfidfMap[numDoc][word]=1
                else:
                    tfidfMap.setdefault(numDoc,{})

            for word in processedref:
                processedrefrences.add(word)
                wordToDocId[word].append(numDoc)
                if numDoc in tfidfMap.keys():
                    if word in tfidfMap[numDoc].keys():
                        tfidfMap[numDoc][word]+=1
                    else:
                        tfidfMap[numDoc][word]=1
                else:
                    tfidfMap.setdefault(numDoc,{})

            for word in processedcats:
                processedcategories.add(word)
                wordToDocId[word].append(numDoc)
                if numDoc in tfidfMap.keys():
                    if word in tfidfMap[numDoc].keys():
                        tfidfMap[numDoc][word]+=1
                    else:
                        tfidfMap[numDoc][word]=1
                else:
                    tfidfMap.setdefault(numDoc,{})

            for word in processedb:
                processedbody.add(word)
                wordToDocId[word].append(numDoc)
                if numDoc in tfidfMap.keys():
                    if word in tfidfMap[numDoc].keys():
                        tfidfMap[numDoc][word]+=1
                    else:
                        tfidfMap[numDoc][word]=1
                else:
                    tfidfMap.setdefault(numDoc,{})

                                
def createIndex():

    global processedInfoBox
    global processedrefrences
    global processedcategories
    global processedbody
    global MyIndex

    for word in processedInfoBox:
        uniqueWords.add(word)
    for word in processedrefrences:
        uniqueWords.add(word)
    for word in processedcategories:
        uniqueWords.add(word)
    for word in processedbody:
        if word.isdigit(): continue
        uniqueWords.add(word)
    for word in processedTitle:
        uniqueWords.add(word)
    
    FinalWords=len(uniqueWords)
    for word in uniqueWords:
        if word in infoBoxcnt.keys():
            infoBoxcnt[str(word)]+=1
        else:
            infoBoxcnt.setdefault(str(word),1)

        if word in processedrefrences:
            if word in refrencescnt.keys():
                refrencescnt[str(word)]+=1
            else:
                refrencescnt.setdefault(word,1)
                
        if word in processedcategories:
            if word in cateogriescnt.keys():
                cateogriescnt[str(word)]+=1
            else:
                cateogriescnt.setdefault(word,1)
                
        if word in processedbody:
            if word in bodycnt.keys():
                bodycnt[str(word)]+=1
            else:
                bodycnt.setdefault(word,1)
        
        if word in processedTitle:
            if word in titlecnt.keys():
                titlecnt[str(word)]+=1
            else:
                titlecnt.setdefault(word,1)

        termFreq=0
        if word in infoBoxcnt.keys():
            termFreq+=infoBoxcnt[str(word)]
        if word in cateogriescnt.keys():
            termFreq+=cateogriescnt[str(word)]
        if word in bodycnt.keys():
            termFreq+=bodycnt[str(word)]
        if word in titlecnt.keys():
            termFreq+=titlecnt[str(word)]

        idfCnt=1
        if word in wordToDocId.keys():
            idfCnt=len(wordToDocId[word])
        logidf=math.log(numDoc/idfCnt)
        termFreq*=logidf

        #docId = next(iter(processedbody))
        docId = wordToDocId[word]
        ans=str(docId)+":"
        if word in titlecnt.keys():
            ans+="t"+str(titlecnt[word])
        else:
            ans+="t0"
        if word in infoBoxcnt.keys():
            ans+="i"+str(infoBoxcnt[word])
        else: ans+="i0"
    
        if word in refrencescnt.keys():
            ans+="r"+str(refrencescnt[word])
        else: ans+="r0"

        if word in cateogriescnt.keys():
            ans+="c"+str(cateogriescnt[word])
        else: ans+="c0"
        
        if word in bodycnt.keys():
            ans+="b"+str(bodycnt[word])
        else: ans+="b0"
        ans+=":"+str(termFreq)
        #print(word+' '+ans)
        MyIndex.setdefault(word,ans)


    for docId in tfidfMap.keys():
        for word in tfidfMap[docId].keys():
            idfcnt=len(wordToDocId[word])
            logcnt=math.log(numDoc/idfcnt)
            tfidfMap[docId][word]*=logcnt


    #print(MyIndex)
    MyIndex = OrderedDict(sorted(MyIndex.items()))
    global initialWords
    outputFolder='/home/rajat/OutputFolder/Index'
    IndexFile = sys.argv[2]
    with open(IndexFile, 'w') as f:
        f.write(json.dumps([MyIndex,tfidfMap,docIDtoTitle]))
    f.close()

    with open(IndexFile,'r') as f:
        data=json.load(f)
        dict1=data[0]
        it = iter(dict1)
        j=0
        for i in range(0, len(dict1),2000):
            chunk= {k:dict1[k] for k in islice(it,2000)}
            json.dump(chunk, open(
            "/home/rajat/OutputFolder/Index" + str(j+1) + ".json", 'w',
            encoding='utf8'), ensure_ascii=False, indent=True)
            j+=1

        dict2=data[1]
        it = iter(dict2)
        for i in range(0, len(dict2),2000):
            chunk= {k:dict2[k] for k in islice(it,2000)}
            #print(type(chunk))
            list1=[]
            list1.append(chunk)
            json.dump(list1, open(
            "/home/rajat/OutputFolder/Index" + str(j+1) + ".json", 'w',
            encoding='utf8'), ensure_ascii=False, indent=True)
            j+=1
        
        dict3=data[2]
        it = iter(dict3)
        for i in range(0, len(dict3),2000):
            chunk= {k:dict3[k] for k in islice(it,2000)}
            list1=[]
            list1.append(chunk)
            json.dump(list1, open(
            "/home/rajat/OutputFolder/Index" + str(j+1) + ".json", 'w',
            encoding='utf8'), ensure_ascii=False, indent=True)
            j+=1    
        

    invertedindex_stat = sys.argv[3]
    with open(invertedindex_stat,'w') as file:
        file.write(str(initialWords))
        file.write("\n")
        file.write(str(FinalWords))    
    file.close()


def main():
    parser = xml.sax.make_parser()
    infile=sys.argv[1]
    handler=Handler()
    parser.setContentHandler(handler)
    parser.parse(infile)
    
if __name__ == "__main__": 
    start = timeit.default_timer()
    main()
    createIndex()
    stop = timeit.default_timer()
    print (stop - start)