var express = require('express')
var router = express.Router()

class PublicRouter {
  static homepage(_, res) {
    return res.render('homepage')
  }

  static getStarted(_, res) {
    res.render('getstarted')
  }

  static uploadPhoto(_, res) {
    res.render('uploadphoto')
  }

  static result(_, res) {
    res.render('result')
  }
}

/* GET home page. */
router.get('/', PublicRouter.homepage)
router.get('/getstarted', PublicRouter.getStarted)
router.get('/uploadphoto', PublicRouter.uploadPhoto)
router.get('/result', PublicRouter.result)

module.exports = router
