# ICS Search

+ It is a Project Assignment for CS 121 (Information Retrieval) at UC Irvine. The project is a search engine searching for pages under domain [ics.uci.edu](ics.uci.edu). 
+ The name ICS comes from School of Information and Computer Science in UC Irvine.

***************************

## Features or Example

+ A search engine from the ground up that is capable of handling tens of thousands of documents or Web pages, under harsh operational constraints and having a query response time under 300ms.
+ Using term-at-a-time during indexing. <strong> Some pages with more than 10000 words are considered as random pages and are ignored. </strong>
+ Using conjunctive processing and multi-threading during searching.



## Requirements

+ [Python3 or later](https://www.python.org/downloads/)
+ [NLTK](https://www.nltk.org/)
+ [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
+ [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/#installation)
+ [Flask Pagination](https://pythonhosted.org/Flask-paginate/)


## Installation or Getting Started

    python3 -m pip install Flask
    python3 -m pip install -U flask-paginate
    python3 -m pip install --user -U nltk
    python3 -m pip install beautifulsoup4
	git clone https://github.com/chengyu2000311/CS171.git
    unzip indexFile.zip
    python3 frontend.py
    open a browser and type localhost:2021

## Demo

![walkThrough](walkThrough.gif)

## Potential Improvement

+ Unable to handle query like masterofcomputerscience.

    + add n-gram algoritm during indexing

+ Didn't add similarity check during indexing
    
## Reference

+ [jxson](https://gist.github.com/jxson) - [README.md](https://gist.github.com/jxson/1784669)



## Contributors

+ Haoyu Cheng, Qiwei He, Runyi Yang



## License
 
The MIT License ([MIT](http://opensource.org/licenses/mit-license.php))

Copyright (c) 2015 Chris Kibble

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
