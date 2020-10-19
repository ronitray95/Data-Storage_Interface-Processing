const bibtexParse = require('bibtex-parse');
const mongo = require('mongodb');
const fs = require('fs');
const bibtex = fs.readFileSync('ACMbibtexs.txt', 'utf8');
//console.log(bibtexParse.entries(bibtex)[0]);
var myJSON = JSON.stringify(bibtexParse.entries(bibtex));