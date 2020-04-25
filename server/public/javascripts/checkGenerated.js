const pollStepFunction = id => {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`https://568efiwqxe.execute-api.us-west-1.amazonaws.com/prod?id=${id}`)
      const data = await response.json()
      console.log(data)

      const { status } = data
      switch (status) {
        case "RUNNING":
          break
        case "SUCCEEDED":
          clearInterval(interval)
          const output = JSON.parse(data.output)
          sessionStorage.setItem("counts", output.counts)
          window.location.href=`/result`
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
  const id = urlParams.get('id')

  pollStepFunction(id)
}

getKeyFromUrl()
