module.exports = {
  spotifyBaseAddress: "https://api.spotify.com",
  clientId: "6ce54085b4164f0fa3928c2b5bfda6d0",
  clientSecret: process.env.CLIENT_SECRET,
  redirectUri: process.env.NODE_ENV === 'development' ? "http://localhost:3000/api/v1/auth/callback" : "https://musaic-project.herokuapp.com/auth/callback",
  s3Bucket: "musaic"
}
