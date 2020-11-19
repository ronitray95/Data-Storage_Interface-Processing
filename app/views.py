from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import FileResponse, HttpResponseRedirect, HttpResponse
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
import time
import codecs
from bs4 import BeautifulSoup as bs
import requests

context = {}


def processFile(request):
    global context
    if request.method == 'POST':
        parser = parseOpts(common_strings=True)
        client = MongoClient(
            "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
        uploaded_file = request.FILES.get('bibfile', '')

        try:
            client.server_info()
            print("server_info():", "OK")

        except errors.ServerSelectionTimeoutError as err:
            print("pymongo ERROR:", err)

        db = client["testDB"]
        bibTexDB = db['bibTex']
        if uploaded_file != '':
            bib_database = parser.parse_file(file=uploaded_file, partial=True)
            for i in range(len(bib_database.entries)):
                if 'doi' in bib_database.entries[i].keys():
                    primkey = bib_database.entries[i].pop('doi')
                else:
                    primkey = bib_database.entries[i].pop('ID')
                bib_database.entries[i]['Yes'] = 0
                bib_database.entries[i]['No'] = 0
                bib_database.entries[i]['Responses'] = []
                bibTexDB.update_one({'_id': primkey},
                                    {'$set': bib_database.entries[i]},
                                    upsert=True)
            print(str(bibTexDB.count_documents({})) + ' docs present')

        myquery = {}
        title_ = request.POST.get('title')
        if title_ != '':
            myquery_str = """{'title':re.compile('.*""" + \
                re.escape(title_)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        author_name = request.POST.get('author')
        if author_name != '':
            myquery_str = """{'author':re.compile('.*""" + \
                re.escape(author_name)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))

        keywords_ = request.POST.get('keywords')
        if keywords_ != '':
            myquery_str = """{'keywords':{ '$all':"""
            myquery_list = []
            temp = keywords_.strip().split(',')
            for temp1 in temp:
                patt = re.compile('.*'+re.escape(temp1)+'.*', re.IGNORECASE)
                myquery_list.append(patt)
            myquery_str += str(myquery_list)
            myquery_str += "}}"
            myquery.update(eval(myquery_str))

        abstract_ = request.POST.get('abstract')
        if abstract_ != '':
            myquery_str = """{'abstract':re.compile('.*""" + \
                re.escape(abstract_)+""".*',re.IGNORECASE)}"""
            myquery.update(eval(myquery_str))
#
        # check for year
        year_start = request.POST.get('year_start')
        if year_start == '':
            year_start = 2000
        year_end = request.POST.get('year_end')
        if year_end == '':
            year_end = datetime.datetime.now().year
        if year_start != '' or year_end != '':
            myquery_str = """{'year':{"$lte":'""" + \
                str(year_end)+"""',"$gte":'"""+str(year_start)+"""'}}"""
            myquery.update(eval(myquery_str))

        language_ = request.POST.get('language')
        if language_ != '':
            patt = re.compile('.*'+re.escape(language_)+'.*', re.IGNORECASE)
            myquery_str = """{ '$or': [ { 'language': { '$exists':False } }, { 'language':patt } ]}"""
            myquery.update(eval(myquery_str))

        publisher_ = request.POST.get('publisher')
        if publisher_ != '':
            patt = re.compile('.*'+re.escape(publisher_)+'.*', re.IGNORECASE)
            myquery_str = """{'$or':[{'publisher':patt  }, { 'booktitle': patt } ] }"""
            myquery.update(eval(myquery_str))

        zipf = zipfile.ZipFile('Output.zip', 'w', zipfile.ZIP_DEFLATED)

        excluded = ''
        content = ''
        for x in bibTexDB.find({}):
            excluding = False
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
                        'Abstract not matching\n'
                    excluding = True
                    continue

            if keywords_ != '':
                temp = keywords_.strip().split(',')
                for temp1 in temp:
                    patt = re.compile(
                        '.*'+re.escape(temp1)+'.*', re.IGNORECASE)
                    if 'keywords' in x.keys() and patt.search(x['keywords']) == None:
                        excluding = True
                        excluded += '\n' + \
                            str(x) + '\n' + 'Keyword not matching\n'
                        continue

            if language_ != '':
                if 'language' in x.keys():
                    # if patt.search(x['language']) != language_:
                    if language_ in x['language']:
                        excluding = True
                        excluded += '\n' + \
                            str(x) + '\n' + 'Language not matching\n'
                        continue

            if publisher_ != '':
                patt = re.compile(
                    '.*'+re.escape(publisher_)+'.*', re.IGNORECASE)
                flag1 = False
                flag2 = False
                if 'publisher' in x.keys() and patt.search(x['publisher']) != None:
                    flag1 = True
                if 'booktitle' in x.keys() and patt.search(x['booktitle']) != None:
                    flag2 = True
                if flag1 == True or flag2 == True:
                    pass
                else:
                    excluding = True
                    excluded += '\n' + \
                        str(x) + '\n' + 'Publisher not matching\n'
                    continue

            if excluding == False:
                content += str(x) + '\n\n'
                url = 'https://scholar.google.com/scholar?lookup=0&q=' + \
                    x['_id']  # +'title:'+str(x['title'])
                # print(url)
                time.sleep(2)
                page = requests.get(url)
                sp = bs(page.content, "html.parser")
                print(page.content)
                #sp = sp.findAll("div", class_="gs_or_ggsm")
                sp = sp.findAll("div", {"class": "gs_or_ggsm"})
                print(sp)
                for s in sp:
                    pdd = s.find('a')['href']
                    response = requests.get(pdd)

                    with open(str(x['_id']).replace("/", "")+'.pdf', 'wb') as f:
                        f.write(response.content)
                        zipf.write(str(x['_id']).replace("/", "")+'.pdf')
                    os.remove(str(x['_id']).replace("/", "")+'.pdf')

        with open('included.txt', 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)

        with open('excluded.txt', 'w', encoding='utf-8', errors='replace') as f:
            f.write(excluded)

        zipf.write('included.txt')
        zipf.write('excluded.txt')
        zipf.close()
        # send_from_directory('./', 'Output.zip', as_attachment=True)
        context = {'bibtex': bibTexDB.find(myquery)}
        return redirect('/assess')
    elif request.method == 'GET':
        return render(request, 'index.html')


def assess(request):
    if request.method == 'POST':
        return FileResponse(open('Output.zip', 'rb'), as_attachment=True, filename='Output.zip')
    return render(request, 'assess.html', context)


def downloadPaper(request):
    if request.method == 'POST':
        return HttpResponse('')
    if request.method == 'GET':
        doi = request.GET.get('doi', 0)
        print('DOI is '+str(doi))
        if doi == 0:
            return HttpResponse('')
        try:
            url = 'https://scholar.google.com/scholar?lookup=0&q=' + \
                str(doi)  # test with 10.1109/MCSE.2007.58
            page = requests.get(url)
            sp = bs(page.content, "html.parser")
            sp = sp.findAll("div", class_="gs_or_ggsm")
            for s in sp:
                pdd = s.find('a')['href']
                if pdd is None:
                    continue
                return HttpResponseRedirect(pdd)
            return HttpResponse('')
        except Exception:
            return HttpResponse('')


def assessment(request):
    client = MongoClient(
        "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
    db = client["testDB"]
    bibTexDB = db['bibTex']
    print(request.POST)
    for key in request.POST.keys():
        if key != 'csrfmiddlewaretoken':
            x = bibTexDB.find_one({"_id": key})
            if request.POST.get(key) == 'Yes':
                x['Yes'] += 1
            elif request.POST.get(key) == 'No':
                x['No'] += 1
            if request.POST.get('r'+str(key)) != '':
                x['Responses'].append(request.POST.get('r'+str(key)))
            bibTexDB.update_one({'_id': key},
                                {'$set': x},
                                upsert=True)
    return redirect('/')
