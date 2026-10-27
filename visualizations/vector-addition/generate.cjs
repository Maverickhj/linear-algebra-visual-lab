'use strict';
const fs = require('node:fs');
const path = require('node:path');
const model = require('./model.js');
const view = require('./view.js');
const target = path.join(__dirname, 'figure.svg');
fs.writeFileSync(target, view.svg(model.compute(model.defaults)) + '\n');
console.log('Generated', target);
