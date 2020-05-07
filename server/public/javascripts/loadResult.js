const getMusaicBucket = () => {
  if (window.location.hostname === 'localhost') {
    return 'musaic'
  } else {
    return 'musaic'
  }
}

const fileName = sessionStorage.getItem('fileName')
const fileUrl = `https://${getMusaicBucket()}.s3-us-west-1.amazonaws.com/generated/${fileName}`

const img = document.getElementById('result-img')
img.src = fileUrl
const resultDiv = document.getElementById('result-with-zoom')
resultDiv.insertBefore(img, resultDiv.firstChild)

new Drift(img, {
  sourceAttribute: 'src',
  paneContainer: document.querySelector('#result-zoom'),
  zoomFactor: 8,
  inlinePane: 900,
  inlineOffsetY: -85,
  containInline: true,
  hoverBoundingBox: true
})

document.getElementById('download').addEventListener('click', () => {
  window.location.href=fileUrl
})
