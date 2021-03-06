var express = require('express')
const _ = require('lodash')
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
          maxAge: data.body['expires_in'] * 1000,
          httpOnly: false
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

  static loading(_, res) {
    res.render('loading')
  }

  static about(_, res) {
    res.render('about')
  }

  static async playlistSelection(req, res, next) {
    try {
      const data = await req.spotifyApi.getUserPlaylists({ limit: 50 })
      res.render('playlistselection', { playlists: data.body.items })
    } catch (err) {
      next(err)
    }
  }

  static async confirmPlaylist(req, res, next) {
    try {
      const data = await req.spotifyApi.getPlaylist(req.params.id)
      const name = data.body["name"]
      const imageUrl = _.get(data, 'body.images[0].url', "https://img.icons8.com/dotty/80/000000/cat-profile.png")

      return res.render('confirmplaylist', { name, imageUrl })
    } catch (err) {
      next(err)
    }
  }

  static result(_, res) {
    res.render('result')
  }
}

/* GET home page. */
router.get('/', PublicRouter.homepage)
// router.get('/getstarted', PublicRouter.getStarted)
router.get('/uploadphoto', PublicRouter.middleware, PublicRouter.uploadPhoto)
router.get('/playlistselection', PublicRouter.middleware, PublicRouter.playlistSelection)
router.get('/confirmplaylist/:id', PublicRouter.middleware, PublicRouter.confirmPlaylist)
router.get('/loading', PublicRouter.loading)
router.get('/result', PublicRouter.result)
router.get('/about', PublicRouter.about)

module.exports = router
