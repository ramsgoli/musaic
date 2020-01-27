const getCookie = name => {
    var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : null;
}

document.getElementById("generate_photo_form").addEventListener('submit', e => {
  e.preventDefault()
  
  // get fileName  from session storage
  const fileName = sessionStorage.getItem("fileName")

  // get playlist id from url
  const splitUrl = window.location.href.split("/")
  const playlistId = splitUrl[splitUrl.length - 1]

  // get access token from cookies
  const accessToken = getCookie("access_token")

  const body = {
    playlist_id: playlist,
    file_name: fileName,
    access_token: accessToken
  }

  // call api with access token
  try {
    const response = await fetch(`/api/v1/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
  } catch (err) {

  }
})
