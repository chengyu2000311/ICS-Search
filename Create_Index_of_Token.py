import json, io
if __name__ == "__main__":
	ind = open("IoT.json", "w")
	ha = dict()
	c = 0
	i = 0
	with io.open("./indexFile/10650TokenDocId.txt", "rt", newline= "\n") as words:
		check = words.readline()
		words.seek(0, 0)
		for line in words:
			x = line.split(" ->")[0]
			print(x)
			ha[x] = c+i
			#i+=1
			c += len(line)

	json.dump(ha, ind)




