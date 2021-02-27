import json, io
if __name__ == "__main__":
	ind = open("DtU.json", "w")
	ha = dict()
	c = 0
	i = 0
	with io.open("indexFile/url_file.txt", "rt", newline= None) as words:
		for word in words:
			word=  word.split(" -> ")
			docid= eval(word[0])
			url = word[1]
			url = url[:-1]
			ha[docid] = url
			print(docid)
	json.dump(ha, ind)
	print(ha[30936])