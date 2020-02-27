const getCookie = name => {
    var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : null;
}

document.getElementById("generate_photo_form").addEventListener('submit', async e => {
  e.preventDefault()
  
  // get fileName  from session storage
  const fileName = sessionStorage.getItem("fileName")

  // get playlist id from url
  const splitUrl = window.location.href.split("/")
  const playlistId = splitUrl[splitUrl.length - 1]

  // get access token from cookies
  const accessToken = getCookie("access_token")

  const body = {
    playlist_id: playlistId,
    file_name: fileName,
    access_token: accessToken
  }

  // call api with access token
  try {
    const response = await fetch(`https://568efiwqxe.execute-api.us-west-1.amazonaws.com/dev`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    window.location.href = `/loading?key=${fileName}`
  } catch (err) {

  }
})
