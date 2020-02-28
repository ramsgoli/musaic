const objectKey = sessionStorage.getItem("fileName")
const img = document.createElement('img')
img.src = `https://musaic.s3-us-west-1.amazonaws.com/generated/${objectKey}`
const resultDiv = document.getElementById('result')
resultDiv.appendChild(img)
