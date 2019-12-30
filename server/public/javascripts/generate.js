document.getElementById("generate_photo_form").addEventListener('submit', e => {
  e.preventDefault()
  
  // get fileName from session storage
  const fileName = sessionStorage.getItem("fileName")

  // get playlist id from url
  const splitUrl = window.location.href.split("/")
  const playlistId = splitUrl[splitUrl.length - 1]

  const body = {
    playlistId,
    fileName
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
