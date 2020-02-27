const express = require('express')
const router = express.Router()
const { spotifyApi } = require('../../../spotify')

class Auth {
  static login(_, res) {
    const scopes = ['user-read-private']
    const authorizeUrl = spotifyApi.createAuthorizeURL(scopes)
    res.redirect(authorizeUrl)
  }

  static async callback(req, res, next) {
    const code = req.query.code
    try {
      const data = await spotifyApi.authorizationCodeGrant(code)

      res.cookie('access_token', data.body['access_token'], {
        maxAge: data.body['expires_in']
      })
      res.cookie('refresh_token', data.body['refresh_token'])
      res.redirect('/uploadphoto')
    } catch (err) {
      next(err)
    }
  }
}

router.get('/login', Auth.login)
router.get('/callback', Auth.callback)

module.exports = router
