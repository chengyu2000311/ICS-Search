import os, time, json, io, multiprocessing, math, heapq
from collections import defaultdict
from threading import Thread
from nltk.stem import SnowballStemmer
from glob import glob

class search():
    def __init__(self, indexFile: str):
        self.stemmer = SnowballStemmer("english")
        self.indexFile = indexFile
        with open(os.path.join('indexFile', "IoT.json"), 'r') as iotfile:
            self.Index_of_Token = json.load(iotfile)
        with open(os.path.join('indexFile', 'DtU.json'), 'r') as duf:
            self.DocId_to_URL = json.load(duf)
        self.numOfDocs = len(self.DocId_to_URL)
        self.stopwords = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}
        # copy from nltk.corpus import stopwords('english')

    def termAtATimeRetrieval(self, Query: str):
        def accOneInvertedList(invertedList: list): # A = {DocID : score}
            doc_num = len(invertedList)
            subA = defaultdict(float)
            for count, value in enumerate(invertedList):
                d = value[1]
                subA[d] = subA[d] + (1 + math.log10(value[0]) * math.log10(self.numOfDocs / doc_num))
            A.append(subA)

        A = [] # A will be a list of dict(DocId : score)
        L = list()
        R = [] # R is a priority queue
        for term in [self.stemmer.stem(x.lower()) for x in Query.split() if x.lower() not in self.stopwords]:
            with open(self.indexFile, newline="\n") as f:
                pos= self.Index_of_Token[term]
                f.seek(pos)
                line = f.readline()
                li = eval(line.split(' -> ')[1]) # get inverted list based on term from index
                L.append(li)
        try:
            allThreads = []
            for invertedList in L:
                allThreads.append(Thread(target=accOneInvertedList, args=(invertedList, )))
            for i in allThreads: i.start()
            for i in allThreads: i.join()
        except:
            print("Error in threads")

        # merge all subA
        finalA = defaultdict(float)
        for i in A:
            for k, v in i.items():
                finalA[k] += v

        for k, v in finalA.items():
            heapq.heappush(R, (-v, k)) # since it is a min-heap, we reverse the score 

        return R

    def start(self, Query: str):
        R = self.termAtATimeRetrieval(Query)
        res = []
        try:
            while True:
                res.append(heapq.heappop(R))
        except IndexError:
            pass
        return [self.DocId_to_URL[str(x[1])] for x in res]



if __name__ == "__main__":
    pass