const bibtexParse = require('bibtex-parse');
const mongo = require('mongodb');
const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
const fs = require('fs');

const bibtex = fs.readFileSync('ACMbibtexs.txt', 'utf8');
//var btJSON = JSON.stringify(bibtexParse.entries(bibtex));
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
        assert.equal(err, null);
        //assert.equal(3, result.result.n);
        //assert.equal(3, result.ops.length);
        console.log(`Inserted ${result.result.length} documents into the collection`);
        callback(result);
    });
}

const findDocuments = function (db, callback) {
    const collection = db.collection('documents');
    collection.find({}).toArray(function (err, docs) {
        assert.equal(err, null);
        console.log("Found the following records");
        console.log(docs)
        callback(docs);
    });
}

const updateDocument = function (db, callback) {
    const collection = db.collection('documents');
    collection.updateOne({ a: 2 }
        , { $set: { b: 1 } }, function (err, result) {
            assert.equal(err, null);
            assert.equal(1, result.result.n);
            console.log("Updated the document with the field a equal to 2");
            callback(result);
        });
}

const removeDocument = function (db, callback) {
    const collection = db.collection('documents');
    collection.deleteMany({}, function (err, result) {
        assert.equal(err, null);
        //assert.equal(1, result.result.n);
        console.log("Removed the document with the field a equal to 3");
        callback(result);
    });
}