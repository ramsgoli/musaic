var express = require('express')
var router = express.Router()
const { createAuthenticatedSpotifyApi } = require('../spotify')

class Users {

  // checks that access token is present
  static async middleware(req, res, next) {
    const spotifyApi = createAuthenticatedSpotifyApi()

    // get access token from cookie
    if (!req.cookies['access_token']) {
      // refresh token
      spotifyApi.setRefreshToken(req.cookies['refresh_token'])
      try {
        const data = await spotifyApi.refreshAccessToken()

        res.cookie('access_token', data.body['access_token'], {
          httpOnly: true,
          maxAge: data.body['expires_in']
        })

        spotifyApi.setAccessToken(data.body['access_token'])
      } catch (err) {
        return next(err)
      }
    } else {
      const access_token = req.cookies['access_token']
      spotifyApi.setAccessToken(access_token)
    }
    req.spotifyApi = spotifyApi
    next()
  }

  static async me(req, res, next) {
    try {
      const data = await req.spotifyApi.getMe()
      const imageUrl = data.body.images[0].url
      res.render('me', { name: data.body["display_name"], image: imageUrl })
    } catch (err) {
      next(err)
    }
  }

  static async playlists(req, res, next) {
    try {
      const data = await req.spotifyApi.getUserPlaylists({ limit: 50 })
      res.send({ data: data.body })
    } catch (err) {
      next(err)
    }
  }
}

router.use(Users.middleware)
router.get('/me', Users.me)
router.get('/me/playlists', Users.playlists)

module.exports = router
