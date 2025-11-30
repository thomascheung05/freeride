function sendAction() {
    const action = document.getElementById('actionSelect').value;

    fetch(`/flask_main?action=${encodeURIComponent(action)}`)
        .then(response => {
            // If response is an image
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("image")) {
                return response.blob();
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data instanceof Blob) {
                const imgUrl = URL.createObjectURL(data);
                document.getElementById('resultImage').src = imgUrl;
            } else if (data) {
                // Only log to console, no popups
                console.log(data.message);
            }
        })
        .catch(err => console.error(err));
}

