const config = require('../config.js')
const SpotifyWebApi = require('spotify-web-api-node')

const spotifyApi = new SpotifyWebApi({
  clientId: config.clientId,
  redirectUri: config.redirectUri,
  clientSecret: config.clientSecret
})

const createAuthenticatedSpotifyApi = () => {
  return new SpotifyWebApi({
    clientId: config.clientId,
    clientSecret: config.clientSecret
  })

  return spotifyApi
}

module.exports = { spotifyApi, createAuthenticatedSpotifyApi }
