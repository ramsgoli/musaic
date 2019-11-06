document.getElementById("upload_photo_form").addEventListener('submit', e => {
  e.preventDefault()
  const files = document.getElementById('file-input').files
  const file = files[0]
  if(file == null){
    return alert('No file selected.')
  }
  getSignedRequest(file)
})

async function getSignedRequest(file){
  const filePrefix = getRandomChars(6)
  const fileName = `${filePrefix}/${file.name}`

  // store filename in session so we can access it in the call to the lambda function
  sessionStorage.setItem("fileName", fileName)
  sessionStorage.setItem()
  try {
    const response = await fetch(`/api/v1/upload/sign-s3?file-name=${fileName}&file-type=${file.type}`)
    if (response.status == 200) {
      const data = await response.json()
      return uploadFile(file, data.signedRequest, data.url) 
    }
  } catch (err) {
    return alert("Please try again later")
  }
}

async function uploadFile(file, signedRequest, url) {
  try {
    const response = await fetch(signedRequest, {
      method: "PUT",
      body: file
    })
    if (response.status != 200) {
      throw new Error()
    }
  } catch (err) {
    return alert("Couldn't Upload file")
  }
}

function getRandomChars(n) {
  let output = ""
  const chars = "abcdefghijklmnopqrstuvwxyz"

  for (let i = 0; i < n; i++) {
    char = chars[Math.floor(Math.random() * chars.length)]
    output += char
  }

  return output
}
