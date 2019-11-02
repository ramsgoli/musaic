var express = require('express')
var router = express.Router()
const { createAuthenticatedSpotifyApi } = require('../../spotify')

class PublicRouter {
  // checks that access token is present
  static async middleware(req, res, next) {
    const spotifyApi = createAuthenticatedSpotifyApi()

    // get access token from cookie
    if (!req.cookies['access_token']) {
      // refresh token
      try {
        spotifyApi.setRefreshToken(req.cookies['refresh_token'])
        const data = await spotifyApi.refreshAccessToken()

        res.cookie('access_token', data.body['access_token'], {
          httpOnly: true,
          maxAge: data.body['expires_in']
        })

        spotifyApi.setAccessToken(data.body['access_token'])
      } catch (err) {
        // redirect to login route
        return res.redirect('/api/v1/auth/login')
      }
    } else {
      const access_token = req.cookies['access_token']
      spotifyApi.setAccessToken(access_token)
    }
    req.spotifyApi = spotifyApi
    next()
  }

  static homepage(_, res) {
    return res.render('homepage')
  }

  static getStarted(_, res) {
    res.render('getstarted')
  }

  static uploadPhoto(_, res) {
    res.render('uploadphoto')
  }

  static async playlistSelection(req, res, next) {
    try {
      const data = await req.spotifyApi.getUserPlaylists({ limit: 50 })
      console.log(data.body.items)
      res.render('playlistselection', { playlists: data.body.items })
    } catch (err) {
      console.log(err)
      next(err)
    }
  }

  static result(_, res) {
    res.render('result')
  }
}

/* GET home page. */
router.get('/', PublicRouter.homepage)
router.get('/getstarted', PublicRouter.getStarted)
router.get('/uploadphoto', PublicRouter.uploadPhoto)
router.get('/playlistselection', PublicRouter.middleware, PublicRouter.playlistSelection)
router.get('/result', PublicRouter.result)

module.exports = router
