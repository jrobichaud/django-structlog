const toastContainer = document.getElementById('toast-container')
const toastTemplate = document.getElementById('toastTemplate');
let abortController = null;

function log(title, url, body, isError, duration) {
  const newToast = toastTemplate.cloneNode(true)

  const text = body ? body.toString() : ""

  if (isError) {
    console.error(title, url, body, duration);
  } else {
    console.log(title, url, body, duration);
  }

  if (isError) {
    newToast.classList.add("border-danger")
  } else {
    newToast.classList.add("border-success")
  }
  newToast.removeAttribute('id');
  const toastHeader = newToast.querySelector('.toast-header > .me-auto');
  toastHeader.textContent = `${title} ${url}`
  if (duration) {
    const toastDuration = newToast.querySelector('.duration');
    toastDuration.textContent = `${duration} ms`
  }
  const toastBody = newToast.querySelector('.toast-body');
  if (body) {
    toastBody.textContent = text.slice(0, 400)
  } else {
    newToast.removeChild(toastBody);
  }
  toastContainer.appendChild(newToast);
  const toast = new bootstrap.Toast(newToast)

  toast.show()
}


async function fetchUrl(url) {
  abortController = new AbortController();
  log("request_started", url);
  const start = new Date();

  try {
    const response = await fetch(url, {
      method: 'get',
      headers: {"Content-Type": "application/json"},
      signal: abortController.signal,
    });
    const text = await response.text();
    if (response.ok) {
      log("request_finished", url, text, false, new Date() - start);
    } else {
      log("request_failed", url, text, true, new Date() - start);
    }
  } catch (err) {
    log("request_failed", url, err, true, new Date() - start);
  }
}


async function fetchStreamingUrl(url) {
  const start = new Date();
  try {
    abortController = new AbortController();
    log("streaming_request_started", url);
    const response = await fetch(url, {
      method: 'get',
      signal: abortController.signal,
    });
    log("streaming_request_finished", url, `Status code ${response.status}`, false, new Date() - start);

    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

    log("streaming_response_started", url, undefined, false, new Date() - start);
    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      log("received", url, value, false, new Date() - start);
    }

    log("streaming_response_finished", url, undefined, false, new Date() - start);
  } catch (err) {
    log("request_failed", url, err, true, new Date() - start);
  }
}

function cancelAsync() {
  if (abortController)
    abortController.abort();
}
