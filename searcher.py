import os, Stemmer, linecache, time, json, io, multiprocessing, math
from nltk.corpus import stopwords

class search():
    def __init__(self, indexFile: str, tf_idfFile: str):
        self.stemmer = Stemmer.Stemmer('english')
        self.indexFile = indexFile
        self.tf_idfFile = tf_idfFile
        with open("IoT.json", 'r') as iotfile:
            self.Index_of_Token = json.load(iotfile)
        with open("DtU.json", 'r') as duf:
            self.DocId_to_URL = json.load(duf)
        self.total_doc = len(self.DocId_to_URL)
        self.stop_words = set(stopwords.words('english'))

    def _getIndexForAllQueries(self, fileName: str, tokens: list) -> list:
        res = list()
        with io.open(fileName, newline= "\n") as f:
            for token in tokens:
                pos = self.Index_of_Token[token]
                f.seek(pos)
                line = f.readline()
                res.append(eval(line.split(' -> ')[1]))
        return res

    def _searchForSingleQuery(self, fileName: str, token: str):
        with io.open(fileName, newline= "\n") as f:
            pos= self.Index_of_Token[token]
            f.seek(pos)
            line = f.readline()
            res = eval(line.split(' -> ')[1])
            return res




    def _merge2Index(self, DocL1: list, DocL2: list) -> list:
        answer = []
        index1, index2 = 0, 0
        while index1 != len(DocL1) and index2 != len(DocL2):
            if DocL1[index1][1] == DocL2[index2][1]:
                answer.append(DocL1[index1])
                index1 += 1
                index2 += 1
            else:
                if DocL1[index1][1] < DocL2[index2][1]:
                    index1 += 1
                else:
                    index2 += 1
        return answer

    def getUrl(self, DocId: list) -> list:
        return [eval(linecache.getline(self.tf_idfFile, int(x) + 1).split(' -> ')[1])[0] for x in DocId]

    def rankThePage(self, Docs: list) -> list:
        try:
            doc_freq = len(Docs)
            buf = [[x[0], x[1]] for x in Docs]
            for i in range(doc_freq):
                buf[i][0] = round((1 + math.log10(buf[i][0]) *  math.log10( self.total_doc/ doc_freq)) , 2)
            answer = sorted(buf, key=lambda x: -(x[0]))
            # Following are for debug in case indexer is wrong
            # for x in Docs:
            #     a = eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1])
            #     if 'acm' not in a[1]:
            #         print(a[0])
            after_sort = time.time()
            res =  [self.DocId_to_URL[str(x[1])] for x in answer]
            return res
        except KeyError:
            print('error')

    def rankBasedOnAnd(self, Docs: list) -> list:
        try:
            doc_freq = len(Docs)
            buf = [[x[0], x[1]] for x in Docs]
            for i in range(doc_freq):
                buf[i][0] = round((1 + math.log10(buf[i][0]) * math.log10(self.total_doc / doc_freq)), 2)
            answer = sorted(buf, key=lambda x: -(x[0]))
            res = [self.DocId_to_URL[str(x[1])] for x in answer]
            return res
        except KeyError:
            print('error')
    def check_stop_word_freq(self, queries: list):
        c = 0
        result = set()
        for word in queries:
            if word in self.stop_words:
                c+=1
            else:
                result.add(word)
        if c/len(queries) > 0.4: #check if needs removing stop words
            return list(set(queries))
        else:
            return list(result)

    def start(self, query: str):
        query = query.lower()
        start = time.time()
        queries = []
        if len(query.split()) > 1:
            queries = [self.stemmer.stemWord(x) for x in query.split()]
        query = self.stemmer.stemWord(query)
        if len(queries) == 0:
            buf = self._searchForSingleQuery(self.indexFile, query)
            mid = time.time()
            print("Spent {} On searching DocID".format(mid-start))
            result = (self.rankThePage(buf))[:5]              
            end = time.time()
            print(f"Spent {end - mid} on sorting.\nCompleted in {end - start} seconds.")
            return result
            end = time.time()
            print(f"completed in {end-start} seconds.")
        else:
            queries = self.check_stop_word_freq(queries)
            allIndexs = self._getIndexForAllQueries(self.indexFile, queries)
            mid = time.time()
            answer = self._merge2Index(allIndexs[0], allIndexs[1])
            for i in range(2, len(queries)):
                answer = self._merge2Index(answer, allIndexs[i])
                # print(self.getUrl(answer[:5]))
            end = time.time()
            #print(answer)
            print("{} spent On searching DocID".format(mid - start))
            print(f"Spent {end - mid} on sorting.\ncompleted in {end - start} seconds.")
            return self.rankBasedOnAnd(answer)[:6]


if __name__ == "__main__":
    searchEni = search("./indexFile/10176TokenDocId.txt", "./indexFile/tf_idfMerge.txt")
    print(searchEni.start("master of computer science"))