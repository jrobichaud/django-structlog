
const toastContainer = document.getElementById('toast-container')
const toastTemplate = document.getElementById('toastTemplate');

function showToast(title, body, isError, duration) {
  const newToast = toastTemplate.cloneNode(true)

  if (isError) {
    newToast.classList.add("border-danger")
  } else {
    newToast.classList.add("border-success")
  }
  newToast.removeAttribute('id');
  const toastHeader = newToast.querySelector('.toast-header > .me-auto');
  toastHeader.textContent = title
  if (duration) {
    const toastDuration = newToast.querySelector('.duration');
    toastDuration.textContent = `${duration} ms`
  }
  const toastBody = newToast.querySelector('.toast-body');
  if (body) {
    toastBody.textContent = body
  }
  else {
    newToast.removeChild(toastBody);
  }
  toastContainer.appendChild(newToast);
  const toast = new bootstrap.Toast(newToast)

  toast.show()
}



function fetchUrl(url) {
  showToast(`request_started ${url}`);
  const start = new Date();


  async function onSuccess(response) {
    const duration = new Date() - start;
    const text = await response.text();
    console.log("request_finished", url, text)
    showToast(`request_finished ${url}`, text, false, duration);
  }

  async function onError(response) {
    const text = await response.text();
    const duration = new Date() - start;
    console.error("request_failed", url, text)
    showToast(`request_failed ${url}`, text.slice(0, 400), true, duration);
  }

  fetch(url, {headers: {"Content-Type": "application/json"},})
    .then(
      async (response) => {
        if (response.ok) {
          await onSuccess(response);
        }
        else {
          await onError(response)
        }
      }
    )
    .catch(
      onError
    )
}
