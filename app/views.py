from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.template import RequestContext
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import bibtexparser as btp
from bibtexparser.bparser import BibTexParser as parseOpts
from pymongo import MongoClient, errors
from werkzeug.utils import secure_filename
import re
import datetime
import os
import json
import zipfile
import sys
import codecs


# def index(request):
#     if request.method == 'GET':
#         return render(request, 'index.html')


def processFile(request):
    if request.method == 'POST':
        parser = parseOpts(common_strings=True)
        client = MongoClient(
            "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
        uploaded_file = request.FILES['file']
        try:
            client.server_info()
            print("server_info():", "OK")

        except errors.ServerSelectionTimeoutError as err:
            print("pymongo ERROR:", err)

        db = client["testDB"]
        bibTexDB = db['bibTex']
        if uploaded_file.name != '':
            # uploaded_file.save(secure_filename(uploaded_file.name))
            x = secure_filename(uploaded_file.name)
            x = default_storage.save(x, ContentFile(uploaded_file.read()))
            with open(x, encoding='utf-8') as bibtex_file:
                bib_database = parser.parse_file(
                    file=bibtex_file, partial=True)

            for i in range(len(bib_database.entries)):
                if 'doi' in bib_database.entries[i].keys():
                    primkey = bib_database.entries[i].pop('doi')
                else:
                    primkey = bib_database.entries[i].pop('ID')
                bibTexDB.update_one({'_id': primkey},
                                    {'$set': bib_database.entries[i]},
                                    upsert=True)
            print(str(bibTexDB.count_documents({})) + ' docs present')

            # os.remove(os.path.join('./', uploaded_file.filename))

        myquery = {}
        querying = False
        title_ = request.POST.get('title')
        if title_ != '':
            querying = True
            myquery_str = """{'title':re.compile('.*""" + \
                re.escape(title_)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        author_name = request.POST.get('author')
        if author_name != '':
            querying = True
            myquery_str = """{'author':re.compile('.*""" + \
                re.escape(author_name)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        keywords_ = request.POST.get('keywords')
        if keywords_ != '':
            querying = True
            myquery_str = """{'keywords':re.compile('.*""" + \
                re.escape(keywords_)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        abstract_ = request.POST.get('abstract')
        if abstract_ != '':
            querying = True
            myquery_str = """{'abstract':re.compile('.*""" + \
                re.escape(abstract_)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        # check for year
        year_start = request.POST.get('year_start')
        if year_start == '':
            year_start = 2000
        year_end = request.POST.get('year_end')
        if year_end == '':
            year_end = datetime.datetime.now().year
        if year_start != '' or year_end != '':
            querying = True
            myquery_str = """{'year':{"$lte":'""" + \
                str(year_end)+"""',"$gte":'"""+str(year_start)+"""'}}"""
            myquery.update(eval(myquery_str))

        excluded = ''
        content = ''
        list_urls = []
        for x in bibTexDB.find({}):
            excluding = False
            # if title_ != '' and x['title'] != title_:
            #    excluded += '\n' + str(x) + '\n' + 'Title not matching\n'

            # print(list(x.keys()))

            if title_ != '':
                patt = re.compile('.*'+re.escape(title_)+'.*', re.IGNORECASE)
                if patt.search(x['title']) == None:
                    excluded += '\n' + str(x) + '\n' + 'Title not matching\n'
                    excluding = True
                    continue

            if author_name != '':
                patt = re.compile(
                    '.*'+re.escape(author_name)+'.*', re.IGNORECASE)

                if patt.search(x['author']) == None:
                    excluded += '\n' + str(x) + '\n' + \
                        'Author name not matching\n'
                    excluding = True
                    continue

            if int(x['year']) < int(year_start) or int(x['year']) > int(year_end):
                excluded += '\n' + str(x) + '\n' + 'Not in given date range\n'
                excluding = True
                continue

            if abstract_ != '':
                patt = re.compile(
                    '.*'+re.escape(abstract_)+'.*', re.IGNORECASE)
                if patt.search(x['abstract']) == None:
                    excluded += '\n' + str(x) + '\n' + \
                        'not matching abstract\n'
                    excluding = True
                    continue

            if keywords_ != '':
                # print(x['doi'])
                patt = re.compile(
                    '.*'+re.escape(keywords_)+'.*', re.IGNORECASE)
                temp = keywords_.strip().split(';')
                for kw in temp:
                    if 'keywords' in x.keys() and patt.search(x['keywords']) == None:
                        excluding = True
                        excluded += '\n' + \
                            str(x) + '\n' + 'keyword not matching\n'

            if excluding == False:
                content += str(x) + '\n\n'

                # print(x.get('url'))

        with open('included.txt', 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)

        with open('excluded.txt', 'w', encoding='utf-8', errors='replace') as f:
            f.write(excluded)

        zipf = zipfile.ZipFile('Output.zip', 'w', zipfile.ZIP_DEFLATED)
        zipf.write('included.txt')
        zipf.write('excluded.txt')
        zipf.close()
        # send_from_directory('./', 'Output.zip', as_attachment=True)
        return FileResponse(open('Output.zip','rb'), as_attachment=True, filename='Output.zip')
    elif request.method == 'GET':
        return render(request, 'index.html')
