
import bibtexparser as btp
from bibtexparser.bparser import BibTexParser as parseOpts
from pymongo import MongoClient, errors
from flask import request, redirect, Response, Flask,render_template
app = Flask(__name__, template_folder='./')

parser = parseOpts(common_strings=True)
# dbuser=admin, pass=admin123
client = MongoClient(
    "mongodb+srv://admin:admin123@cluster0.ajwby.mongodb.net/testDB?retryWrites=true&w=majority")
# parser.homogenize_fields=True
with open("inputBibTex/SSD bibtexts ACM.txt") as bibtex_file:
    # bib_database = btp.load(bibtex_file) #use this for well defined strings, entries like month=Jan will raise Exception
    # put partial =false for default behaviour
    bib_database = parser.parse_file(file=bibtex_file, partial=True)

# print(bib_database.strings)
# print(bib_database.entries)
try:
    client.server_info()
    print("server_info():", "OK")

except errors.ServerSelectionTimeoutError as err:
    # catch pymongo.errors.ServerSelectionTimeoutError
    print("pymongo ERROR:", err)

db = client["testDB"]
bibTexDB = db['bibTex']

bibTexDB.insert_many(bib_database.entries)

client.close()


@app.route('/giveData', methods=['POST'])
def giveData():
    data = request.form['data']
    print('The data is: '+data)
    return render_template('index.html')


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
