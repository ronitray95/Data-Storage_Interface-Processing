
import bibtexparser as btp
from bibtexparser.bparser import BibTexParser as parseOpts
from pymongo import MongoClient, errors
from flask import request, redirect, Response, Flask, render_template, url_for
app = Flask(__name__, template_folder='./')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def giveData():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
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

        # gonna delete everything then insert
        x = bibTexDB.delete_many({})
        print(x.deleted_count, " docs deleted")

        y = bibTexDB.insert_many(bib_database.entries)
        print(len(y.inserted_ids), " docs inserted")

        client.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
