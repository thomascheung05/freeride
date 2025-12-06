// Global vars
let map;
let smallMap;
let smallrouteLayer;
let routeLayer;
let smallbikeMarker = null;
let bigbikeMarker = null;
let freerideInterval = null;
document.addEventListener("DOMContentLoaded", initUI);
document.getElementById("getWindowsButton").addEventListener("click", fetchVisibleWindows);
document.getElementById("windowsmodalClose").addEventListener("click", () => {document.getElementById("getWindowsModal").classList.add("hidden");});
document.getElementById("getbbox").addEventListener("click", getBbox);
document.getElementById("bboxmodalClose").addEventListener("click", () => {document.getElementById("getBboxModal").classList.add("hidden");});
document.getElementById("savePreset").addEventListener("click", savePreset);
document.getElementById("processRoute").addEventListener("click", processRoute);
document.getElementById("startRoute").addEventListener("click", freerideRun);
document.getElementById("stopRoute").addEventListener("click", async () => {
    try {
        // Stop polling on the client side
        if (freerideInterval) {
            clearInterval(freerideInterval);
            freerideInterval = null;
            console.log("Freeride runner stopped (client).");
        }
        const defaultImgSrc = "/static/img/duck.jpg"; // replace with your default image
        const imageElems = ["image", "smallImage"];
        imageElems.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.src = defaultImgSrc;
        });

        // Optionally reset the map marker
        if (smallbikeMarker) smallbikeMarker.remove();
        if (bigbikeMarker) bigbikeMarker.remove();
        // Tell the backend to clear globals
        const response = await fetch("/api/freeride_stop", { method: "POST" });
        const data = await response.json();
        console.log("Server response:", data.message);



    } catch (err) {
        console.error("Error stopping freeride:", err);
    }
});

async function freerideRun() {
    const userPresetName = document.getElementById("userPresetName").value;
    const userRoute = document.getElementById("userRoute").value;
    const startDist = document.getElementById("startDist").value;

    const response = await fetch("/api/freeride_run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            preset_name: userPresetName,
            route: userRoute,
            start_dist: startDist
        })
    });

    const data = await response.json();

    // Remove previous layers if they exist
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    if (smallrouteLayer) {
        smallMap.removeLayer(smallrouteLayer);
    }

    // Add route to main map
    routeLayer = L.geoJSON(data.route, {
        style: {
            color: 'orange', // set color to orange
            weight: 3
        }
    }).addTo(map);

    // Snap main map to the first point of the route
    const firstCoord = data.route.features[0].geometry.coordinates[0]; // [lng, lat]
    map.setView([firstCoord[1], firstCoord[0]], 15); // 15 is zoom level

    // Add route to small map
    smallrouteLayer = L.geoJSON(data.route, {
        style: {
            color: 'orange', // set color to orange
            weight: 3
        }
    }).addTo(smallMap);

    // Snap small map to the first point of the route
    smallMap.setView([firstCoord[1], firstCoord[0]], 15);

    // Create a bicycle icon
    const bikeIcon = L.icon({
        iconUrl: '/static/img/bike.jpg', // replace with your bicycle image path
        iconSize: [32, 32], // adjust size as needed
        iconAnchor: [16, 16] // anchor so it points at the coordinate
    });

    // Place the bicycle marker at the first point
    smallbikeMarker = L.marker([firstCoord[1], firstCoord[0]], { icon: bikeIcon }).addTo(smallMap);
    bigbikeMarker = L.marker([firstCoord[1], firstCoord[0]], { icon: bikeIcon }).addTo(smallMap);


    // Start polling for position updates
    

    pollPosition(); // first immediate call
    freerideInterval = setInterval(pollPosition, 10000); // store interval ID
}


async function pollPosition() {
    try {
        const response = await fetch("/api/get_position");
        const data = await response.json();
        console.log("Position update:", data);

        if (data.image) {
            document.getElementById("image").src =
                "data:image/png;base64," + data.image;
        }
        if (data.image) {
            document.getElementById("smallImage").src =
                "data:image/png;base64," + data.image;
        }
        if (smallbikeMarker && data.lat && data.lon) {
            smallbikeMarker.setLatLng([data.lat, data.lon]);
        }
        if (bigbikeMarker && data.lat && data.lon) {
            bigbikeMarker.setLatLng([data.lat, data.lon]);
        }

    } catch (err) {
        console.error("Polling error:", err);
    }
}


async function processRoute(){
    const userRouteToProcess = document.getElementById("userRouteToProcess").value;

    const response = await fetch("/api/process_route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            route_to_process: userRouteToProcess}
        )
    });
    const data = await response.json();
    console.log(data);
}


async function savePreset(){
    const userConfigPresetName = document.getElementById("userConfigPresetName").value;
    const windowName = document.getElementById("userWindow").value;
    const userDistBbox = document.getElementById("userDistBbox").value;
    const userSpeedBbox = document.getElementById("userSpeedBbox").value;
    const response = await fetch("/api/save_preset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            preset_name: userConfigPresetName,
            distbbox: userDistBbox,
            speedbbox: userSpeedBbox,
            window_name: windowName
        })
    });

    const data = await response.json();
    console.log(data);
}


async function getBbox(){
    const windowName = document.getElementById("userWindow").value;

    const response = await fetch("/api/get_bbox", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ window_name: windowName })
    });

    const data = await response.json();
    console.log(data);
    showbboxModal(data.screenshot); // pass the base64 string

    function showbboxModal(imageBase64) {  // use the correct parameter
        const bboxmodal = document.getElementById("getBboxModal");
        const bboxModalText = document.getElementById("bboxModalText");

        // Insert the image
        bboxModalText.innerHTML = `<img src="data:image/png;base64,${imageBase64}" style="max-width:100%; max-height:80vh;">`;
        bboxmodal.classList.remove("hidden");
    }
}


async function fetchVisibleWindows() {

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Function to run function and display all the windows to know what window has our data
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    try {
        const response = await fetch("/api/get_window");
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        const data = await response.json();
        console.log("Visible windows:", data.formatted_windows);

        // Do something with the data, e.g., update the UI
        showWindowsModal(data.formatted_windows)
        function showWindowsModal(message) {
            ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            // Open a modal with a message
            ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            const modal = document.getElementById("getWindowsModal");
            const modalText = document.getElementById("modalText");
            modalText.innerHTML = message.replace(/\n/g, "<br>");
            modal.classList.remove("hidden");
        }
    } catch (err) {
        console.error("Error fetching windows:", err);
    }
}


async function initUI() {
    
    const response = await fetch("/api/init_ui");
    if (!response.ok) {
        throw new Error("Network response was not ok");
    }
    const data = await response.json();

    // NEW: populate dropdowns
    fillDropDown("userPresetName", data.config_presets);
    fillDropDown("userRouteToProcess", data.unprocessed_files);
    fillDropDown("userRoute", data.processed_files);

    function fillDropDown(id, items) {
        const select = document.getElementById(id);
        select.innerHTML = ""; // clear existing options

        // Add placeholder first
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.disabled = true;
        placeholder.selected = true;  // Important! Keeps it selected
        placeholder.textContent = id === "userRoute" ? "Route" : "Config Preset";
        select.appendChild(placeholder);

        // Add folder items
        items.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item;
            opt.textContent = item;
            select.appendChild(opt);
        });
    }



    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Initializes the big and small map (one is always hidden)
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Fullscreen map
    map = L.map('map', { zoomControl: false }).setView([45.5017, -73.5673], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    // Small map
    smallMap = L.map('smallMap', { zoomControl: false }).setView([45.5017, -73.5673], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(smallMap);

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Switch wether image or map is full screen / in mini viewer
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    const mainImage = document.getElementById("image");
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
