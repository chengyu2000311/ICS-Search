from flask import Flask, render_template, request
from searcher import search
app=Flask(__name__)


@app.route('/')
def index():
    query = request.args.get('query')
    urls = ['Result Place holder'] * 5
    searchEni = search("./indexFile/10176TokenDocId.txt", "./indexFile/tf_idfMerge.txt")
    if query != None and query!= "":
        urls = searchEni.start(query)
    query = "Enter here" if query == None else query
    print(urls)
    return render_template("index.html", one=urls[0], two=urls[1], three=urls[2],
        four=urls[3],five=urls[4], query=query)


if __name__=="__main__":
    app.run(port=2021,host="127.0.0.1",debug=True)
