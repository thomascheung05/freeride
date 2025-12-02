document.addEventListener("DOMContentLoaded", initUI);
document.getElementById("getWindowsButton").addEventListener("click", fetchVisibleWindows);
document.getElementById("windowsmodalClose").addEventListener("click", () => {document.getElementById("getWindowsModal").classList.add("hidden");});
document.getElementById("getbbox").addEventListener("click", getBbox);
document.getElementById("bboxmodalClose").addEventListener("click", () => {document.getElementById("getBboxModal").classList.add("hidden");});
document.getElementById("savePreset").addEventListener("click", savePreset);
document.getElementById("processRoute").addEventListener("click", processRoute);
document.getElementById("startRoute").addEventListener("click", freerideRun);




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
    console.log("Route Loaded:", data);

    // Start polling for position updates
    pollPosition();
    setInterval(pollPosition, 5000);
}


async function pollPosition() {
    try {
        const response = await fetch("/api/get_position");
        const data = await response.json();
        console.log("Position update:", data);

        // update UI here...

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
