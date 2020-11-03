
import bibtexparser as btp
from bibtexparser.bparser import BibTexParser as parseOpts
from pymongo import MongoClient, errors
from flask import request, redirect, Response, Flask, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
import re
import datetime
import os
import json
app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def giveData():
    parser = parseOpts(common_strings=True)
    client = MongoClient(
        "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
    uploaded_file = request.files['file']
    try:
        client.server_info()
        print("server_info():", "OK")

    except errors.ServerSelectionTimeoutError as err:
        print("pymongo ERROR:", err)

    db = client["testDB"]
    bibTexDB = db['bibTex']
    if uploaded_file.filename != '':
        uploaded_file.save(secure_filename(uploaded_file.filename))

        with open(uploaded_file.filename, encoding='utf-8') as bibtex_file:
            bib_database = parser.parse_file(file=bibtex_file, partial=True)

        for i in range(len(bib_database.entries)):
            if 'doi' in bib_database.entries[i].keys():
                primkey = bib_database.entries[i].pop('doi')
            else:
                primkey = bib_database.entries[i].pop('ID')
            bibTexDB.update_one({'_id': primkey},
                                {'$set': bib_database.entries[i]},
                                upsert=True)
        print(str(bibTexDB.count_documents({})) + ' docs present')

        #os.remove(os.path.join('./', uploaded_file.filename))

    myquery = {}
    querying = False
    title_ = request.form.get('title')
    if title_ != '':
        querying = True
        myquery_str = """{'title':re.compile('.*""" + \
            re.escape(title_)+""".*',re.IGNORECASE)}"""
        myquery.update(eval(myquery_str))

    author_name = request.form.get('author')
    if author_name != '':
        querying = True
        myquery_str = """{'author':re.compile('.*""" + \
            re.escape(author_name)+""".*',re.IGNORECASE)}"""
        myquery.update(eval(myquery_str))

    keywords_ = request.form.get('keywords')
    if keywords_ != '':
        querying = True
        myquery_str = """{'keywords':re.compile('.*""" + \
            re.escape(keywords_)+""".*',re.IGNORECASE)}"""
        myquery.update(eval(myquery_str))

    abstract_ = request.form.get('abstract')
    if abstract_ != '':
        querying = True
        myquery_str = """{'abstract':re.compile('.*""" + \
            re.escape(abstract_)+""".*',re.IGNORECASE)}"""
        myquery.update(eval(myquery_str))

    # check for year
    year_start = request.form.get('year_start')
    if year_start == '':
        year_start = 2000
    year_end = request.form.get('year_end')
    if year_end == '':
        year_end = datetime.datetime.now().year
    if year_start != '' or year_end != '':
        querying = True
        myquery_str = """{'year':{"$lte":'""" + \
            str(year_end)+"""',"$gte":'"""+str(year_start)+"""'}}"""
        myquery.update(eval(myquery_str))

    if querying==True:
        print(myquery)
        short_list = list(bibTexDB.find(myquery))
        client.close()

        # write result to file
        with open('youroutput.txt', 'w', encoding="utf-8") as f:
            for line in short_list:
                f.write(str(line))
                f.write('\n')

    # send the file with resultant bibtex back to user
    if querying:
        return send_from_directory('./', 'youroutput.txt', as_attachment=True)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
