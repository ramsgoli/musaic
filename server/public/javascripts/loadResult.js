const fileName = sessionStorage.getItem('fileName')
const fileUrl = `https://musaic.s3-us-west-1.amazonaws.com/generated/${fileName}`

const img = document.createElement('img')
img.src = fileUrl
const resultDiv = document.getElementById('result')
resultDiv.appendChild(img)

document.getElementById('download').addEventListener('click', () => {
  window.location.href=fileUrl
})
