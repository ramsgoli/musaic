const express = require('express')
const router = express.Router()
const config = require('../config.json')
const querystring = require('querystring')

router.get('/login', (req, res, next) => {
  const scopes = 'user-read-private user-read-email'
  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: config.clientId,
      scope: scopes,
      redirect_uri: config.redirectUri
    })
  )
})

module.exports = router
