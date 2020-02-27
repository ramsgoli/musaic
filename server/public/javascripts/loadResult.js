const urlParams = new URLSearchParams(window.location.search)
const objectKey = urlParams.get('key')
const img = document.createElement('img')
img.src = `https://musaic.s3-us-west-1.amazonaws.com/generated/${objectKey}`
const resultDiv = document.getElementById('result')
resultDiv.appendChild(img)
