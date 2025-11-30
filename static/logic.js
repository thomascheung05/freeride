window.addEventListener('DOMContentLoaded', () => {
    // Initialize Leaflet map
    var map = L.map('map').setView([45.5017, -73.5673], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    const mainSidebar = document.getElementById('mainSidebar');
    const ssSidebar = document.getElementById('ssSidebar');
    const windowList = document.getElementById('windowList');

    // Swap sidebar buttons
    document.getElementById('ssSidebarButton').addEventListener('click', () => {
        mainSidebar.classList.add('d-none');
        ssSidebar.classList.remove('d-none');
    });

    document.getElementById('backToMain').addEventListener('click', () => {
        ssSidebar.classList.add('d-none');
        mainSidebar.classList.remove('d-none');
        windowList.innerHTML = ""; // Clear list when going back
    });
    
    // Fetch windows from Flask
    document.getElementById('getAllWindows').addEventListener('click', () => {
        fetch(`/flask_main?action=find_casting_window`)
            .then(response => response.json())
            .then(data => {
                // Clear previous list
                windowList.innerHTML = "";

                // Assume Flask returns an array of window names
                data.windows.forEach(win => {
                    const li = document.createElement('li');
                    li.textContent = win;
                    li.className = "list-group-item";
                    windowList.appendChild(li);
                });
            })
            .catch(err => console.error(err));
    });


}); // ← this closes the DOMContentLoaded event listener




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
