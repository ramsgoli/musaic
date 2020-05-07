["one", "two", "three"].forEach(id => {
  const photo = document.getElementById(id)

  photo.addEventListener('click', e => {
    e.preventDefault() 

    const fileName = `preloaded/${getRandomChars(5)}/${id}.jpeg`
    sessionStorage.setItem("fileName", fileName) 

    window.location.href = '/playlistselection'
  })
})
