document.addEventListener("DOMContentLoaded", initUI);






function initUI() {
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Initializes the big and small map (one is always hidden)
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Fullscreen map
    const map = L.map('map', { zoomControl: false }).setView([45.5017, -73.5673], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    // Small map
    const smallMap = L.map('smallMap', { zoomControl: false }).setView([45.5017, -73.5673], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(smallMap);

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Switch wether image or map is full screen / in mini viewer
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    const mainImage = document.getElementById("sideImage");
    const smallImage = document.getElementById("smallImage");
    const swapButton = document.getElementById("swapButton");
    swapmapimage(mainImage,smallImage,swapButton);
    function swapmapimage(mainImage,smallImage,swapButton){
        let mapIsFullscreen = true;

        swapButton.addEventListener("click", () => {
            if (mapIsFullscreen) {
                // Map → small window
                document.getElementById("map").style.display = "none";
                mainImage.style.display = "block";

                document.getElementById("smallMap").style.display = "block";
                smallImage.style.display = "none";

                mapIsFullscreen = false;
            } else {
                // Image → small window
                document.getElementById("map").style.display = "block";
                mainImage.style.display = "none";

                document.getElementById("smallMap").style.display = "none";
                smallImage.style.display = "block";

                mapIsFullscreen = true;
            }

            map.invalidateSize();
            smallMap.invalidateSize();
        });
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Open and close the main sidebar
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    const menuButton = document.getElementById("menuButton");
    const sidePanel = document.getElementById("sidePanel");
    opensidepan(menuButton, sidePanel);
    function opensidepan(menuButton, sidePanel) {
        menuButton.addEventListener("click", () => {
            const isHidden = getComputedStyle(sidePanel).display === "none";
            sidePanel.style.display = isHidden ? "block" : "none";
        });
    }
    return map;
}











// var map = L.map('map').setView([45.5017, -73.5673], 12);
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     attribution: '© OpenStreetMap contributors'
// }).addTo(map);








// window.addEventListener('DOMContentLoaded', () => {
//     // Initialize Leaflet map

    
//     const mainSidebar = document.getElementById('mainSidebar');
//     const ssSidebar = document.getElementById('ssSidebar');
//     const windowList = document.getElementById('windowList');

//     // Swap sidebar buttons
//     document.getElementById('ssSidebarButton').addEventListener('click', () => {
//         mainSidebar.classList.add('d-none');
//         ssSidebar.classList.remove('d-none');
//     });

//     document.getElementById('backToMain').addEventListener('click', () => {
//         ssSidebar.classList.add('d-none');
//         mainSidebar.classList.remove('d-none');
//         windowList.innerHTML = ""; // Clear list when going back
//     });
    
//     // Fetch windows from Flask
//     document.getElementById('getAllWindows').addEventListener('click', () => {
//         fetch(`/flask_main?action=find_casting_window`)
//             .then(response => response.json())
//             .then(data => {
//                 // Clear previous list
//                 windowList.innerHTML = "";

//                 // Assume Flask returns an array of window names
//                 data.windows.forEach(win => {
//                     const li = document.createElement('li');
//                     li.textContent = win;
//                     li.className = "list-group-item";
//                     windowList.appendChild(li);
//                 });
//             })
//             .catch(err => console.error(err));
//     });


// }); // ← this closes the DOMContentLoaded event listener




// function sendAction() {
//     const action = document.getElementById('actionSelect').value;

//     fetch(`/flask_main?action=${encodeURIComponent(action)}`)
//         .then(response => {
//             // If response is an image
//             const contentType = response.headers.get("content-type");
//             if (contentType && contentType.includes("image")) {
//                 return response.blob();
//             } else {
//                 return response.json();
//             }
//         })
//         .then(data => {
//             if (data instanceof Blob) {
//                 const imgUrl = URL.createObjectURL(data);
//                 document.getElementById('resultImage').src = imgUrl;
//             } else if (data) {
//                 // Only log to console, no popups
//                 console.log(data.message);
//             }
//         })
//         .catch(err => console.error(err));
// }
