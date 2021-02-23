import os, json
from bs4 import BeautifulSoup
from glob import glob
import Stemmer
from urllib.parse import urlparse
import hashlib

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
	py_stemmer = Stemmer.Stemmer('english')
	result = [py_stemmer.stemWord(x.lower()) for x in re.findall("[a-zA-Z0-9]+[a-zA-Z0-9]+", text)]
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

class indexer():
	# Input is the parent directory of all json files
	# generate two txt file one with docID -> [url, [term frequencies]], the other with token -> [freq, [docID]]

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
		samecount =0
		try:
			fileName0, fileName1, urlId = 0, 0, 0  # fileName0 is for token->[freq, [docID]], fileName1 is for docID -> [url, [term frequencies]]
			for i in getAllJsonFile(self.dirWithJson):
				if len(self.indexDocID) > 1000:
					if os.path.exists(indexDir + f'\\{fileName0}TokenDocId.txt'):
						os.remove(indexDir + f'\\{fileName0}TokenDocId.txt')
					for k, v in self.indexDocID.items():  # sort all docID list
						self.indexDocID[k][1] = sorted(v[1])
					with open(indexDir + f'\\{fileName0}TokenDocId.txt', 'w') as wf:
						for k, v in sorted(self.indexDocID.items()):  # sort dict based on token
							wf.write(f'{k} -> {v}\n')
					self.indexDocID.clear()
					fileName0 += 1

				if len(self.tf_idf) > 200:
					if os.path.exists(indexDir + f'\\{fileName1}tf_idf.txt'):
						os.remove(indexDir + f'\\{fileName1}tf_idf.txt')
					with open(indexDir + f'\\{fileName1}tf_idf.txt', 'w') as wf:
						for k, v in sorted(self.tf_idf.items()):
							wf.write(f'{k} -> {v}\n')
					self.numOfDocs += len(self.tf_idf)
					self.tf_idf.clear()
					fileName1 += 1

				with open(i, 'r') as jsonF:
					data = json.load(jsonF)
					content = data['content'] if 'content' in data else 0
					if type(content) != str: continue
					soup = BeautifulSoup(content, 'html.parser')
					# remove fragment
					link = data["url"] if 'content' in data else 0
					parsed = urlparse(link)
					if parsed.fragment != '':
						link = link.split('#')[0]
					if (link not in self.urls and link != 0):
						self.urls.add(link)
					else:
						print("Found duplicate Link: {}".format(link))
						fragcount+=1
						continue
					# find exact duplicate
					md5 = get_MD5(content)
					if md5 in hashes:
						print("Found duplicate Content: {}, MD5: {}".format(link, md5))
						samecount +=1
						continue
					else:
						hashes.add(md5)

					#
					freq = computeWordFrequencies(tokenize2(soup.get_text()))
					self.tf_idf[urlId] = [link, freq]

					for k, v in freq.items():
						if k in self.indexDocID:
							self.indexDocID[k][0] += v
							self.indexDocID[k][1].append(urlId)
						else:
							self.indexDocID[k] = [v, [urlId]]
					urlId += 1

		except:
			raise

		finally:
			print(len(self.indexDocID), len(self.tf_idf))
			for k, v in self.indexDocID.items():  # sort all docID list
				self.indexDocID[k][1] = sorted(v[1])

			with open(indexDir + f'\\{fileName0}TokenDocId.txt', 'w') as wf:
				for k, v in sorted(self.indexDocID.items()):  # sort dict based on token and write to files
					wf.write(f'{k} -> {v}\n')

			with open(indexDir + f'\\{fileName1}tf_idf.txt', 'w') as wf:
				self.numOfDocs += len(self.tf_idf)
				for k, v in sorted(self.tf_idf.items()):
					wf.write(f'{k} -> {v}\n')
			print("Dup link: {}, Dup content: {}".format(fragcount, samecount))
			self.merge_all_file(indexDir)

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
					new_list = [first_list[0] + second_list[0], sorted(first_list[1] + second_list[1])]
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

	def merge_all_file(self, indexDir):
		os.chdir(indexDir)
		self.fileIndex = len(glob("*TokenDocId.txt"))
		num = 0
		total_line = 0
		while True:
			self.merge_2_file(f'{num}TokenDocId.txt', f'{num + 1}TokenDocId.txt')
			num += 2
			if num == self.fileIndex - 1:
				break

		with open(f'{self.fileIndex - 1}TokenDocId.txt') as rf:
			for _ in rf.readlines():
				self.numOfTokens += 1

		with open('tf_idfMerge.txt', 'w') as wf:
			for i in sorted(glob('*tf_idf.txt'), key=lambda x: int(x.split('tf')[0])):
				with open(i, 'r') as rf:
					wf.write(rf.read())

		for tf in glob("*tf_idf.txt"):
			os.remove(tf)


if __name__ == "__main__":
	Index = indexer('C:\\Users\\Dinnerhe\\Documents\\CS121\\CS121_Assignment3\\DEV')  # Directory of DEV
	Index.buildIndex()
	# Index.merge_all_file('/Users/chenghaoyu/Desktop/CS 121/assignments/assignment3/CS121_Assignment3/indexFile.old2')
	print('Number of unique token:', Index.numOfTokens)
	print('Number of docs:', Index.numOfDocs)

	#8690 http://flamingo.ics.uci.edu/releases/4.1/src/lbaktree/data/data.txt