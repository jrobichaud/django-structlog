function fetchUrl(url) {

  fetch(url, {headers: {"Content-Type": "application/json"},})
    .then(
      async (response) => {
        if (response.ok)
          console.log("request_finished", url, await response.text())
        else
          console.error("request_failed", url, await response.text())
      }
    )
    .catch(
      (response) => console.error("request_failed", url, response)
    )

}
