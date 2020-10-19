const bibtexParse = require('bibtex-parse');
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
const fs = require('fs');

const bibtex = fs.readFileSync('ACMbibtexs.txt', 'utf8');
var bt = bibtexParse.entries(bibtex);
console.log(typeof(bt));

const url = 'mongodb://localhost:27017';
const dbName = 'myproject';
const client = new MongoClient(url);
var deletion = false;

client.connect(function (err) {
    assert.equal(null, err);
    console.log("Connected successfully to server");

    const db = client.db(dbName);
    insertDocuments(db, bt, function () {
        findDocuments(db, function () {
            if (deletion)
                removeDocument(db, function () { });
            client.close();
        });
    });
});

const insertDocuments = function (db, data, callback) {
    const collection = db.collection('documents');
    collection.insertMany(data, function (err, result) {
        console.log(`Inserted ${result.result.length} documents into the collection`);
        callback(result);
    });
}

const findDocuments = function (db, callback) {
    const collection = db.collection('documents');
    collection.find({}).toArray(function (err, docs) {
        console.log("Found the following records");
        console.log(docs)
        callback(docs);
    });
}

const removeDocument = function (db, callback) {
    const collection = db.collection('documents');
    collection.deleteMany({}, function (err, result) {
        callback(result);
    });
}