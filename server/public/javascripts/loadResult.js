const urlParams = new URLSearchParams(window.location.search)
const img = document.createElement('img')
img.src = urlParams.get('key')
const resultDiv = document.getElementById('result')
resultDiv.appendChild(img)

document.getElementById('download').addEventListener('click', () => {
  window.location.href=urlParams.get('key')
})
