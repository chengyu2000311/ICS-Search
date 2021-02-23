import os, Stemmer, linecache, time, json, io

class search():
    def __init__(self, indexFile: str, tf_idfFile: str):
        self.stemmer = Stemmer.Stemmer('english')
        self.indexFile = indexFile
        self.tf_idfFile = tf_idfFile
        with open("IoT.json", 'r') as iotfile:
            self.Index_of_Token = json.load(iotfile)
    
    def _getIndexForAllQueries(self, fileName: str, tokens: list) -> list:
        res = [None]*len(tokens)
        with io.open(fileName, newline= "\n") as f:
            for token in tokens:
                pos = self.Index_of_Token[token]
                f.seek(pos)
                line = f.readline()
                print(line)
                res.append(eval(line.split(' -> ')[1])[1])
        return res

    def _searchForSingleQuery(self, fileName: str, token: str):
        with io.open(fileName, newline= "\n") as f:
            pos= self.Index_of_Token[token]
            f.seek(pos)
            line = f.readline()
            return eval(line.split(' -> ')[1])[1]

    def _merge2Index(self, DocL1: list, DocL2: list) -> list:
        answer = []
        index1, index2 = 0, 0
        while index1 != len(DocL1) and index2 != len(DocL2):
            if DocL1[index1] == DocL2[index2]:
                answer.append(DocL1[index1])
                index1 += 1
                index2 += 1
            else:
                if DocL1[index1] < DocL2[index2]:
                    index1 += 1
                else: index2 += 1
        return answer

    def getUrl(self, DocId: list) -> list:
        return [eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1])[0] for x in DocId]

    def rankThePage(self, Docs: list, query: str) -> list:
        try:
            #print(eval(linecache.getline(self.tf_idfFile, 2+1).split(' -> ')[1])[1]['acm'])
            answer = sorted([eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1]) for x in Docs], key=lambda x:-(x[1][query]))
            # Following are for debug in case indexer is wrong
            # for x in Docs:
            #     a = eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1])
            #     if 'acm' not in a[1]:
            #         print(a[0])

            return [x[0] for x in answer]
        except KeyError:
            print('error')

    def rankBasedOnAnd(self, Docs: list, queries: list) -> list:
        try:
            answer = sorted([eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1]) for x in Docs], key=lambda x:-sum([x[1][query] for query in queries]))
            # Following are for debug in case indexer is wrong
            # for x in Docs:
            #     a = eval(linecache.getline(self.tf_idfFile, int(x)+1).split(' -> ')[1])
            #     for q in queries:
            #         if q not in a[1]:
            #             print(a[0])
            return [x[0] for x in answer]
        except KeyError:
            print('error')


    def start(self, query: str):
        query = query.lower()
        start = time.time()
        queries = []
        if len(query.split()) > 1:
            queries = [self.stemmer.stemWord(x) for x in query.split()]
        query = self.stemmer.stemWord(query)
        if len(queries) == 0:
                #print(self._searchForSingleQuery(self.indexFile, query)[:5])
                #print(self.getUrl(self._searchForSingleQuery(self.indexFile, query)[:5]))
            return ((self.rankThePage(self._searchForSingleQuery(self.indexFile, query), query))[:5])
            end = time.time()
            print(f"completed in {end-start} seconds.")
        else:
            allIndexs = self._getIndexForAllQueries(self.indexFile, queries)
            answer = self._merge2Index(allIndexs[0], allIndexs[1])
            for i in range(2, len(queries)):
                answer = self._merge2Index(answer, allIndexs[i])
                #print(self.getUrl(answer[:5]))
            return (self.rankBasedOnAnd(answer, queries)[:5])
            end = time.time()
            print(f"completed in {end-start} seconds.")

if __name__ == "__main__":
    searchEni = search("./CS121_Assignment3/indexFile/10924TokenDocId.txt", "./CS121_Assignment3/indexFile/tf_idfMerge.txt")
    searchEni.start()