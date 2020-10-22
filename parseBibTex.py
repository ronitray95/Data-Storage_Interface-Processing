
import bibtexparser as btp
from bibtexparser.bparser import BibTexParser as parseOpts
from pymongo import MongoClient, errors
from flask import request, redirect, Response, Flask, render_template, url_for
from werkzeug.utils import secure_filename
import re
app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def giveData():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(secure_filename(uploaded_file.filename))
        parser = parseOpts(common_strings=True)
        client = MongoClient(
            "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
        with open(uploaded_file.filename, encoding='utf-8') as bibtex_file:
            bib_database = parser.parse_file(file=bibtex_file, partial=True)

        try:
            client.server_info()
            print("server_info():", "OK")

        except errors.ServerSelectionTimeoutError as err:
            print("pymongo ERROR:", err)

        db = client["testDB"]
        bibTexDB = db['bibTex']

        for i in range(len(bib_database.entries)):
            if 'doi' in bib_database.entries[i].keys():
                primkey = bib_database.entries[i].pop('doi')
            else:
                primkey = bib_database.entries[i].pop('ID')
            bibTexDB.update_one({'_id': primkey},
                                {'$set': bib_database.entries[i]},
                                upsert=True)
        print(str(bibTexDB.count_documents({})) + ' docs present')

        


        author_name=request.form.get('author')
        if author_name !='':
        
            myquery = { "author": re.compile(  ".*"+re.escape(author_name)+".*", re.IGNORECASE ) }
            author_list=bibTexDB.find(myquery)
            for author_list_el in author_list:
                print(author_list_el)

            
        client.close()

    return redirect(url_for('index'))
    


if __name__ == "__main__":
    app.run(debug=True)
