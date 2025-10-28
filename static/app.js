document.addEventListener('DOMContentLoaded', (event) => {
    // Connect to the Socket.IO server
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // --- NEW: Get Buttons ---
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const btnSettings = document.getElementById('btn-settings'); // (Not used yet)

    // Get other DOM elements
    const videoStream = document.getElementById('video-stream');
    const metricVolume = document.getElementById('metric-volume');
    const metricDistance = document.getElementById('metric-distance');
    const metricResponse = document.getElementById('metric-response');
    
    const statusOpen = document.getElementById('status-open');
    const statusPinch = document.getElementById('status-pinch');
    const statusClosed = document.getElementById('status-closed');

    const statusMap = {
        'Open Hand': statusOpen,
        'Pinch': statusPinch,
        'Closed': statusClosed
    };
    
    // --- NEW: Set Initial Button State ---
    btnStop.disabled = true;
    btnStart.disabled = false;
    videoStream.style.display = 'none'; // <-- 1. HIDE VIDEO INITIALLY

    // --- NEW: Button Click Listeners ---
    btnStart.addEventListener('click', () => {
        console.log('Start button clicked');
        socket.emit('start_stream');
        btnStart.disabled = true;
        btnStop.disabled = false;
        videoStream.style.display = 'block'; // <-- 2. SHOW VIDEO ON START
        videoStream.alt = "Loading video stream...";
    });

    btnStop.addEventListener('click', () => {
        console.log('Stop button clicked');
        socket.emit('stop_stream');
        btnStart.disabled = false;
        btnStop.disabled = true;
        videoStream.src = ""; // Clear the last frame
        videoStream.style.display = 'none'; // <-- 3. HIDE VIDEO ON STOP
        videoStream.alt = "Stream paused. Press Start.";
    });

    // --- SocketIO Listeners ---

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    // Handle video frame updates
    socket.on('video_frame', (data) => {
        videoStream.src = 'data:image/jpeg;base64,' + data.image;
    });

    // Handle data updates for metrics, gestures, and graph
    socket.on('update_data', (data) => {
        // 1. Update Metrics
        metricVolume.innerText = `${Math.round(data.volume)}%`;
        metricDistance.innerText = `${Math.round(data.distance)}mm`;
        metricResponse.innerText = `${data.response_time}ms`;

        // 2. Update Gesture Status
        Object.values(statusMap).forEach(el => el.classList.remove('active'));
        
        if (statusMap[data.gesture]) {
            statusMap[data.gesture].classList.add('active');
            statusMap[data.gesture].querySelector('.status-label').innerText = 'Active';
        }
        
        Object.entries(statusMap).forEach(([key, el]) => {
            if (key !== data.gesture) {
                el.querySelector('.status-label').innerText = 'Inactive';
            }
        });

        // 3. Update Chart
        updateChart(data.volume, data.distance);
    });

    // --- Chart.js Setup ---
    const ctx = document.getElementById('volumeChart').getContext('2d');
    const volumeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Timestamps
            datasets: [
                {
                    label: 'Volume %',
                    data: [],
                    borderColor: 'rgba(255, 69, 0, 1)',
                    backgroundColor: 'rgba(255, 69, 0, 0.2)',
                    yAxisID: 'y-volume',
                    tension: 0.1
                },
                {
                    label: 'Distance (mm)',
                    data: [],
                    borderColor: 'rgba(0, 123, 255, 1)',
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    yAxisID: 'y-distance',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: {
                        display: false 
                    }
                },
                'y-volume': {
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Volume %'
                    }
                },
                'y-distance': {
                    type: 'linear',
                    position: 'right',
                    min: 0,
                    max: 300, 
                    title: {
                        display: true,
                        text: 'Distance (mm)'
                    },
                    grid: {
                        drawOnChartArea: false, 
                    },
                }
            }
        }
    });

    function updateChart(volume, distance) {
        const MAX_DATA_POINTS = 30;
        const now = new Date().toLocaleTimeString();

        volumeChart.data.labels.push(now);
        volumeChart.data.datasets[0].data.push(volume);
        volumeChart.data.datasets[1].data.push(distance);

        if (volumeChart.data.labels.length > MAX_DATA_POINTS) {
            volumeChart.data.labels.shift();
            volumeChart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
        }
        volumeChart.update('none'); 
    }
});