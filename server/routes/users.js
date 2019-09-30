var express = require('express')
var router = express.Router()
const { createAuthenticatedSpotifyApi } = require('../spotify')

/* GET users listing. */
class Users {
  static async me(req, res, next) {
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

    try {
      const data = await spotifyApi.getMe()
      res.send({ data: data.body })
    } catch (err) {
      next(err)
    }
  }

  static async playlists(req, res, next) {
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

    try {
      const data = await spotifyApi.getUserPlaylists()
      res.send({ data: data.body })
    } catch (err) {
      next(err)
    }
  }
}

router.get('/me', Users.me)
router.get('/me/playlists', Users.playlists)

module.exports = router
