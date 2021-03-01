import hashlib
import math
import os, json
import time, io
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from glob import glob
from nltk.stem import SnowballStemmer


def getAllJsonFile(dirPath: str):
    try:
        os.chdir(dirPath)
        if len(glob('*.json')) != 0:
            for i in glob('*.json'):
                yield os.path.abspath(i)

        if len(glob(dirPath + '/*/')) != 0:
            for dir in glob(dirPath + '/*/'):
                for i in getAllJsonFile(dir):
                    yield os.path.abspath(i)
    except:
        print("Probably the dirPath is false")
        raise


def tokenize2(text: str) -> list:
    import re
    result = []
    snowball_stemmer = SnowballStemmer("english")
    for x in re.findall("[a-zA-Z0-9]+[a-zA-Z0-9]+", text):
        result.append(snowball_stemmer.stem(x.lower()))
    return result


def computeWordFrequencies(tokenList: list) -> dict:
    result = {}
    for token in tokenList:
        if token not in result:
            result.update({token: 1})
        else:
            result[token] += 1
    return result


def get_MD5(content: str):
    md = hashlib.md5()
    md.update(content.encode("utf-8"))
    return md.hexdigest()


class indexer:
    def __init__(self, dirWithJson: str):
        self.indexDocID = dict()
        self.tf_idf = dict()
        self.dirWithJson = dirWithJson
        self.fileIndex = 0
        self.numOfDocs = 0
        self.numOfTokens = 0
        self.urls = set()

    def buildIndex(self):
        if os.path.exists('indexFile'):
            os.rmdir('indexFile')
        os.mkdir('indexFile')
        os.chdir('indexFile')
        indexDir = os.getcwd()
        hashes = set()
        fragcount = 0
        samecount = 0
        try:
            fileName0, urlId = 0, 0  # fileName0 is for token->[freq, [docID]], fileName1 is for docID -> [url,
            # [term frequencies]]
            url_file = open(os.path.join(indexDir, 'url_file.txt'), 'w')
            for i in getAllJsonFile(self.dirWithJson):
                if len(self.indexDocID) > 1000:
                    if os.path.exists(os.path.join(indexDir, f'{fileName0}TokenDocId.txt')):  
                        os.remove(os.path.join(indexDir, f'{fileName0}TokenDocId.txt'))
                    with open(os.path.join(indexDir, f'{fileName0}TokenDocId.txt'), 'w') as wf:
                        for k, v in sorted(self.indexDocID.items()):  # sort dict based on token
                            wf.write(f'{k} -> {v}\n')
                    self.indexDocID.clear()
                    fileName0 += 1

                with open(i, 'r') as jsonF:
                    check_duplicate = True
                    data = json.load(jsonF)
                    content = data['content'] if 'content' in data else 0
                    if type(content) != str: continue
                    soup = BeautifulSoup(content, 'html.parser')
                    # remove fragment
                    link = data["url"] if 'content' in data else 0
                    parsed = urlparse(link)
                    if parsed.fragment != '':
                        link = link.split('#')[0]
                    if link not in self.urls and link != 0:
                        self.urls.add(link)
                    else:
                        print("Found duplicate Link: {}".format(link))
                        fragcount += 1
                        check_duplicate = False
                        continue
                    # find exact duplicate
                    md5 = get_MD5(content)
                    if md5 in hashes:
                        print("Found duplicate Content: {}, MD5: {}".format(link, md5))
                        samecount += 1
                        check_duplicate = False
                        continue
                    else:
                        hashes.add(md5)
                    if check_duplicate:
                        content = soup.get_text() # first get all content into memory
                        for tag in soup.find_all(['h1', 'h2', 'strong']): # find all tag h1 and strong
                            content += f' {tag.get_text()}'*5 # add in the end of content and pass to tokenize2
                        freq = computeWordFrequencies(tokenize2(content))

                        for k, v in freq.items():
                            if k in self.indexDocID:
                                self.indexDocID[k].append((v, urlId))
                            else:
                                self.indexDocID[k] = [(v, urlId)]
                        url_file.write(f'{urlId} -> {link}\n')
                        urlId += 1

        except:
            raise

        finally:
            with open(os.path.join(indexDir, f'{fileName0}TokenDocId.txt'), 'w') as wf:
                for k, v in sorted(self.indexDocID.items()):  # sort dict based on token
                    wf.write(f'{k} -> {v}\n')
            url_file.close()
            print("Dup link: {}, Dup content: {}".format(fragcount, samecount))
            self.numOfDocs = urlId
            self.merge_all_file(indexDir)
            self.createIndexOfToken()
            self.createDocIdtoURI()

    def merge_2_file(self, num1, num2):
        file1 = open(num1)
        file2 = open(num2)
        new_merge_file = open(f'{self.fileIndex}TokenDocId.txt', 'w')
        self.fileIndex += 1
        line1 = file1.readline()
        line2 = file2.readline()
        while line1 != '' or line2 != '':
            if line1 != '' and line2 != '':
                split1 = line1.split(" -> ")
                split2 = line2.split(" -> ")
                if split1[0] == split2[0]:
                    first_list, second_list = eval(split1[1]), eval(split2[1])
                    new_list = first_list + second_list
                    new_merge_file.write(f'{split1[0]} -> {new_list}\n')
                    line1 = file1.readline()
                    line2 = file2.readline()
                elif split1[0] < split2[0]:
                    new_merge_file.write(line1)
                    line1 = file1.readline()
                else:
                    new_merge_file.write(line2)
                    line2 = file2.readline()
            elif line1 == '':
                new_merge_file.write(line2)
                line2 = file2.readline()

            elif line2 == '':
                new_merge_file.write(line1)
                line1 = file1.readline()

        file1.close()
        file2.close()
        new_merge_file.close()
        os.remove(num1)
        os.remove(num2)

    def createIndexOfToken(self):
        ind = open('IoT.json', "w")
        ha = dict()
        c = 0
        i = 0
        with io.open(glob("*TokenDocId.txt")[0], "rt", newline="\n") as words:
            check = words.readline()
            words.seek(0, 0)
            for line in words:
                x = line.split(" ->")[0]
                print(x)
                ha[x] = c+i
                c += len(line)
        json.dump(ha, ind)

    def createDocIdtoURI(self):
        ind = open('DtU.json', "w")
        ha = dict()
        c = 0
        i = 0
        with io.open("url_file.txt", "rt", newline= None) as words:
            for word in words:
                word=  word.split(" -> ")
                docid= eval(word[0])
                url = word[1]
                url = url[:-1]
                ha[docid] = url
                print(docid)
        json.dump(ha, ind)

    def merge_all_file(self, indexDir):
        os.chdir(indexDir)
        self.fileIndex = len(glob("*TokenDocId.txt"))
        num = 0
        while True:
            self.merge_2_file(f'{num}TokenDocId.txt', f'{num + 1}TokenDocId.txt')
            num += 2
            if num == self.fileIndex - 1:
                break

if __name__ == "__main__":
    index = indexer(r'/Users/chenghaoyu/Desktop/CS 121/assignments/assignment3/ANALYST')
    index.buildIndex()

