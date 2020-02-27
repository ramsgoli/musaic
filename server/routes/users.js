var express = require('express')
var router = express.Router()
const _ = require('lodash')
const { createAuthenticatedSpotifyApi } = require('../spotify')


class Users {

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
          maxAge: data.body['expires_in']
        })

        spotifyApi.setAccessToken(data.body['access_token'])
      } catch (err) {
        // redirect to login route
        return res.redirect('/auth/login')
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
      const imageUrl = _.get(data, 'body.images[0].url', "https://img.icons8.com/dotty/80/000000/cat-profile.png")
      res.render('me', {
        name: data.body["display_name"],
        image: imageUrl,
        followers: data.body["followers"],
        email: data.body["email"]
      })
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
