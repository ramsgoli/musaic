const pollS3 = key => {
  const interval = setInterval(() => {
    const promise = fetch(`https://musaic.s3-us-west-1.amazonaws.com/generated/${key}`, {
      method: "HEAD"
    })
    const status = promise.then(data => {
      console.log(data.status)
      if (data.status === 200) {
        clearInterval(interval)
        window.location.href=`/result?key=${key}`
      }
    })
  }, 1000)
}

const getKeyFromUrl = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const objectKey = urlParams.get('key')

  pollS3(objectKey)
}

getKeyFromUrl()
