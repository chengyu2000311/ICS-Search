from flask import Flask, render_template, request
from searcher import search
app=Flask(__name__)



@app.route('/')
def index():
    query = request.args.get('query')
    searchEni = search("./indexFile/10924TokenDocId.txt", "./indexFile/tf_idfMerge.txt")
    while True:
        if query != None:
            urls = searchEni.start(query)
        return render_template("index.html", one=urls[0], two=urls[1], three=urls[2],
        four=urls[3],five=urls[4])  #加入变量传递


if __name__=="__main__":
    app.run(port=2021,host="127.0.0.1",debug=True)
