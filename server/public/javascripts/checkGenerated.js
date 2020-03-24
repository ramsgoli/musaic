const pollStepFunction = arn => {
  const params = {
    executionArn: arn
  }

  const interval = setInterval(async () => {
    try {
      const response = await fetch(`https://568efiwqxe.execute-api.us-west-1.amazonaws.com/dev?executionArn=${arn}`)
      const data = await response.json()
      console.log(data)

      const { status } = data
      switch (status) {
        case "RUNNING":
          break
        case "SUCCEEDED":
          clearInterval(interval)
          const output = JSON.parse(data.output)
          const body = JSON.parse(output.body)
          console.log(body)
           window.location.href=`/result?key=${body.object_url}`
          break
        default:
          clearInterval(interval)
          alert("Failed to generate your musaic. Please try again")
          break
      }
    } catch (err) {
      console.log(err)
    }
  }, 2000)
}

const getKeyFromUrl = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const arn = urlParams.get('arn')

  pollStepFunction(arn)
}

getKeyFromUrl()
