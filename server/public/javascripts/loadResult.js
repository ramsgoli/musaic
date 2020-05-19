const getMusaicBucket = () => {
  if (window.location.hostname === 'localhost') {
    return 'musaic-dev'
  } else {
    return 'musaic'
  }
}

const getFileUrl = () => {
  let fileName = sessionStorage.getItem('fileName')
  if (fileName.startsWith("preloaded")) {
    fileName = fileName.replace("preloaded/", "")
  }
  return fileUrl = `https://${getMusaicBucket()}.s3-us-west-1.amazonaws.com/generated/${fileName}`
}

const insertImgTag = () => {
  const img = document.getElementById('result-img')
  img.src = getFileUrl()
  const resultDiv = document.getElementById('result-with-zoom')
  resultDiv.insertBefore(img, resultDiv.firstChild)

  return img
}

const initializeDrift = (img) => {
  new Drift(img, {
    sourceAttribute: 'src',
    paneContainer: document.querySelector('#result-zoom'),
    zoomFactor: 12,
    inlinePane: 900,
    inlineOffsetY: -85,
    containInline: true,
    hoverBoundingBox: true
  })
}

const initializeDownloadButton = () => {
  document.getElementById('download').addEventListener('click', () => {
    window.location.href = getFileUrl()
  })
}

const initializeTopAlbums = () => {
  const topAlbums = JSON.parse(sessionStorage.getItem('topAlbums'))
  const resultZoomContainer = document.getElementById('result-zoom')
  for (album in topAlbums) {
    const topAlbumDiv = document.createElement('div')
    topAlbumDiv.className = "top-album-div"

    const nameParagraphTag = document.createElement('p')
    const nameNode = document.createTextNode(topAlbums[album]['name'])
    nameParagraphTag.appendChild(nameNode)

    const imageTag = document.createElement('img')
    imageTag.src = topAlbums[album]['url']

    topAlbumDiv.append(imageTag,nameParagraphTag)
    resultZoomContainer.appendChild(topAlbumDiv)
  }
}

const run = () => {
  const img = insertImgTag()
  initializeDrift(img)
  initializeDownloadButton()
  initializeTopAlbums()
}

run()
