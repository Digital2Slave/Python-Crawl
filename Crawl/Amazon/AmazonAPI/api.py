#!/usr/loca/bin/python
#-*- encoding:utf-8 -*-

from flask import Flask, request, jsonify
from flask.ext.restful import Resource, Api
from spider import parse

app = Flask(__name__)

@app.route('/book', methods=['GET'])
def get():
    isbnvalue = request.args.get('isbn')
    bookdict  = parse(isbnvalue)
    return jsonify({'isbn':bookdict})

if __name__ == '__main__':
    #app.run(debug=True) # Defalut 127.0.0.1:5000
    app.run(debug=False,host='192.168.100.3', port=5001)
    #app.run(debug=False,host='192.168.31.187', port=5001)
