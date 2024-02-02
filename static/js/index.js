let eventSource;
let sessionToken = generateSessionToken();
console.log('current sessionToken:', sessionToken)

var resetButton = document.getElementById('resetButton');
resetButton.addEventListener('click', function() {
    sessionToken = generateSessionToken();
    const imageContainer = document.getElementById('imageContainer');
    imageContainer.innerHTML = '';
    console.log('reset sessionToken, current sessionToken:', sessionToken)
});

function startFetching() {
    if (eventSource) {
        eventSource.close();
    }

    const query = document.getElementById('queryInput').value.trim();
    if (query === '') {
        if (eventSource) {
            eventSource.close();
        }
        return;
    }

    let amount = document.getElementById('amountInput').value.trim();
    amount = amount === '' ? 20 : parseInt(amount);

    var siteselectElement = document.getElementById("sourceSelect");
    var siteValue = siteselectElement.options[siteselectElement.selectedIndex].value;

    eventSource = new EventSource(`${applicationRoot}/api/Crawler?site=${siteValue}&query=${query}&amount=${amount}&sessionToken=${sessionToken}`);

    eventSource.onmessage = function(event) {
        if (event.data === 'CLOSE') {
            console.log('EventSource connection closed');
            eventSource.close();
        } else {
            const img_name = event.data;
            loadImageFromBackend(img_name, sessionToken);
        }
    };
}

function loadImageFromBackend(img_name, sessionToken) {
    // Send GET request to backend to get image
    fetch(`${applicationRoot}/api/GetImage?sessionToken=${sessionToken}&img_name=${encodeURIComponent(img_name)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        const objectURL = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = objectURL;
        link.target = "_blank";

        const img = new Image();
        img.onload = function() {
            img.style.maxWidth = "200px";
            img.style.height = "auto";
        };
        img.onerror = function() {
            console.error('Error loading image');
        };
        img.src = objectURL;
        link.appendChild(img);

        const imageContainer = document.getElementById('imageContainer');
        imageContainer.appendChild(link);
    })
    .catch(error => {
        console.error('Error fetching image:', error);
    });
}

function generateSessionToken() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

var downloadButton = document.getElementById('downloadButton');
downloadButton.addEventListener('click', function() {
    fetch(`${applicationRoot}/api/SessionImage?sessionToken=${sessionToken}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'images.zip';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error downloading images:', error);
    });
});
