/**
* This is a self-contained module that defines its routes, callbacks, models and views
* all internally. Such approach to code organization follows the recommendations of TJ:
*
* http://vimeo.com/56166857
* 
*/

// Libraries
var express = require('express')
  , app = exports = module.exports = express();

// Don't just use, but also export in case another module needs to use these as well.
exports.callbacks    = require('./controllers/analysis');
exports.models       = require('./models');

//-- For increased module encapsulation, you could also serve templates with module-local 
//-- paths, but using shared layouts and partials may become tricky
//var hbs = require('hbs');
//app.set('views', __dirname + '/views');
//app.set('view engine', 'handlebars');
//app.engine('handlebars', hbs.__express);

// Module's Routes. Note this is actually under wherever the module is attached
app.get('/', exports.callbacks.render);

