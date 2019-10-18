var express = require('express')
var router = express.Router()

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('homepage')
})

router.get('/getstarted', function(req, res) {
  res.render('getstarted')
})

router.get('/uploadphoto', function(req, res) {
  res.render('uploadphoto')
})

router.get('/result', function(req, res) {
  res.render('result')
})

module.exports = router
