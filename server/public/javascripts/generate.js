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

  const input = {
    playlist_id: playlistId,
    file_name: fileName,
    access_token: accessToken
  }

  const body = {
    input: JSON.stringify(input),
    stateMachineArn: "arn:aws:states:us-west-1:048178349693:stateMachine:MyStateMachine"
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

    const data = await response.json()

    window.location.href = `/loading?arn=${data.executionArn}`
  } catch (err) {

  }
})
