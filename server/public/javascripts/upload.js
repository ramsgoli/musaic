document.getElementById("upload_photo_form").addEventListener('submit', e => {
  e.preventDefault()
  console.log("HERE")
  const files = document.getElementById('file-input').files
  const file = files[0]
  if(file == null){
    return alert('No file selected.')
  }
  getSignedRequest(file)
})

async function getSignedRequest(file){
  try {
    const response = await fetch(`/api/v1/upload/sign-s3?file-name=${file.name}&file-type=${file.type}`)
    if (response.status == 200) {
      const data = await response.json()
      return uploadFile(file, data.signedRequest, data.url) 
    }
  } catch (err) {
    return alert("Please try again later")
  }
}

async function uploadFile(file, signedRequest, url){
  try {
    const response = await fetch(signedRequest, {
      method: "PUT",
      body: file
    })
    if (response.status === 200) {
      console.log("Your photo was uploaded successfully")
      alert('redirecting your ass')
    }
  } catch (err) {
    return alertt("Couldn't Upload file")
  }
}
