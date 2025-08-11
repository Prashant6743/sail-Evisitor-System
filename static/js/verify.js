document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const video = document.getElementById('scanner-video');
    const cameraSelect = document.getElementById('camera-select');
    const startCamera = document.getElementById('start-camera');
    const cameraToggle = document.getElementById('camera-toggle');
    const resultContainer = document.getElementById('result-container');
    const manualInput = document.getElementById('application-id');
    const manualButton = document.getElementById('manual-verify');
    const qrModeBtn = document.getElementById('qr-mode-btn');
    const uploadModeBtn = document.getElementById('upload-mode-btn');
    const manualModeBtn = document.getElementById('manual-mode-btn');
    const qrMode = document.getElementById('qr-mode');
    const uploadMode = document.getElementById('upload-mode');
    const manualMode = document.getElementById('manual-mode');
    const scannerInfo = document.querySelector('.scanner-info');
    const uploadBox = document.getElementById('upload-box');
    const qrUpload = document.getElementById('qr-upload');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const retryUpload = document.getElementById('retry-upload');

    let selectedDeviceId = null;
    let codeReader = null;
    let isScanning = false;

    // Initialize ZXing code reader
    const initCodeReader = async () => {
        try {
            codeReader = new ZXing.BrowserMultiFormatReader();
            
            // Get available video devices
            const videoInputDevices = await navigator.mediaDevices.enumerateDevices();
            const cameras = videoInputDevices.filter(device => device.kind === 'videoinput');
            
            if (cameras.length === 0) {
                throw new Error('No cameras found on this device');
            }

            // Update camera selection dropdown
            cameraSelect.innerHTML = cameras.map(camera =>
                `<option value="${camera.deviceId}">${camera.label || `Camera ${cameras.indexOf(camera) + 1}`}</option>`
            ).join('');
            
            // Select the back camera if available
            const backCamera = cameras.find(camera => camera.label.toLowerCase().includes('back'));
            selectedDeviceId = backCamera ? backCamera.deviceId : cameras[0].deviceId;
            cameraSelect.value = selectedDeviceId;

            return true;
        } catch (err) {
            console.error('Failed to initialize code reader:', err);
            scannerInfo.textContent = `Scanner initialization failed: ${err.message}`;
            return false;
        }
    };

    // Start the scanner
    const startScanner = async () => {
        if (isScanning) return;

        try {
            if (!codeReader) {
                if (!await initCodeReader()) return;
            }

            isScanning = true;
            scannerInfo.textContent = 'Starting camera...';
            startCamera.textContent = 'Stop Camera';
            
            // Stop any existing streams
            await stopScanner();
            
            // Configure video constraints
            const constraints = {
                video: {
                    deviceId: selectedDeviceId,
                    facingMode: "environment",
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    aspectRatio: { ideal: 1.777777778 }
                }
            };

            // Start video stream
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            await video.play();

            // Start decoding
            await codeReader.decodeFromVideoDevice(selectedDeviceId, video, (result, err) => {
                if (result) {
                    console.log('Code detected:', result);
                    handleScanResult(result.text);
                }
                if (err && !(err instanceof ZXing.NotFoundException)) {
                    console.error('Scan error:', err);
                }
            });

            scannerInfo.textContent = 'Scanning for QR codes and barcodes...';
            
            // Check if flash is available
            const track = stream.getVideoTracks()[0];
            if (track.getCapabilities().torch) {
                cameraToggle.style.display = 'block';
            }
        } catch (err) {
            console.error('Failed to start scanner:', err);
            scannerInfo.textContent = `Failed to start camera: ${err.message}. Please check camera permissions.`;
            startCamera.textContent = 'Start Camera';
            isScanning = false;
        }
    };

    // Stop the scanner
    const stopScanner = async () => {
        if (!isScanning) return;

        try {
            // Stop video stream
            const tracks = video.srcObject?.getTracks() || [];
            tracks.forEach(track => track.stop());
            video.srcObject = null;

            // Reset code reader
            if (codeReader) {
                await codeReader.reset();
            }

            scannerInfo.textContent = 'Click "Start Camera" to begin scanning';
            startCamera.textContent = 'Start Camera';
            isScanning = false;
        } catch (err) {
            console.error('Failed to stop scanner:', err);
        }
    };

    // Handle image upload
    const handleImageUpload = async (file) => {
        if (!file) return;

        try {
            // Show preview
            const reader = new FileReader();
            reader.onload = async (e) => {
                previewImage.src = e.target.result;
                uploadBox.style.display = 'none';
                previewContainer.style.display = 'block';

                try {
                    // First try client-side QR code detection
                    const img = new Image();
                    img.src = e.target.result;
                    await img.decode(); // Ensure image is loaded

                    // Create a canvas to draw the image
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    // Get image data for processing
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    let qrResult = null;
                    
                    // Try client-side detection first
                    if (!codeReader) {
                        codeReader = new ZXing.BrowserMultiFormatReader();
                    }

                    try {
                        const result = codeReader.decode(imageData);
                        if (result) {
                            qrResult = result.text;
                        }
                    } catch (decodeErr) {
                        console.log('Client-side QR detection failed, trying server-side...');
                    }

                    if (qrResult) {
                        // If we got a result client-side, verify it
                        handleScanResult(qrResult);
                    } else {
                        // If client-side failed, send to server for processing
                        const response = await fetch('/verify_api/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                image: e.target.result,
                                name: file.name
                            })
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }

                        const data = await response.json();
                        if (data.status === 'success') {
                            handleScanResult(data.gatepass.application_id);
                        } else {
                            throw new Error(data.message || 'Failed to process image');
                        }
                    }
                } catch (err) {
                    console.error('Failed to process image:', err);
                    resultContainer.className = 'result-container error';
                    resultContainer.style.display = 'block';
                    resultContainer.innerHTML = `
                        <div class="result-title">❌ Error</div>
                        <div>${err.message || 'Could not detect a QR code in the image. Please try a different image.'}</div>
                    `;
                }
            };
            reader.readAsDataURL(file);
        } catch (err) {
            console.error('Failed to handle image upload:', err);
            resultContainer.className = 'result-container error';
            resultContainer.style.display = 'block';
            resultContainer.innerHTML = `
                <div class="result-title">❌ Error</div>
                <div>Failed to process the image. Please try again.</div>
            `;
        }
    };

    // Mode switching functions
    const switchToQRMode = () => {
        qrMode.classList.add('active');
        uploadMode.classList.remove('active');
        manualMode.classList.remove('active');
        qrModeBtn.classList.add('active');
        uploadModeBtn.classList.remove('active');
        manualModeBtn.classList.remove('active');
        resultContainer.style.display = 'none';
    };

    const switchToUploadMode = () => {
        uploadMode.classList.add('active');
        qrMode.classList.remove('active');
        manualMode.classList.remove('active');
        uploadModeBtn.classList.add('active');
        qrModeBtn.classList.remove('active');
        manualModeBtn.classList.remove('active');
        resultContainer.style.display = 'none';
        stopScanner();
    };

    const switchToManualMode = () => {
        manualMode.classList.add('active');
        qrMode.classList.remove('active');
        uploadMode.classList.remove('active');
        manualModeBtn.classList.add('active');
        qrModeBtn.classList.remove('active');
        uploadModeBtn.classList.remove('active');
        resultContainer.style.display = 'none';
        stopScanner();
        manualInput.focus();
    };

    // Event Listeners
    qrModeBtn.addEventListener('click', switchToQRMode);
    uploadModeBtn.addEventListener('click', switchToUploadMode);
    manualModeBtn.addEventListener('click', switchToManualMode);

    startCamera.addEventListener('click', () => {
        if (isScanning) {
            stopScanner();
        } else {
            startScanner();
        }
    });

    cameraSelect.addEventListener('change', async (event) => {
        selectedDeviceId = event.target.value;
        if (isScanning) {
            await stopScanner();
            await startScanner();
        }
    });

    // File upload handling
    qrUpload.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleImageUpload(e.target.files[0]);
        }
    });

    retryUpload.addEventListener('click', () => {
        uploadBox.style.display = 'block';
        previewContainer.style.display = 'none';
        qrUpload.value = '';
        resultContainer.style.display = 'none';
    });

    // Drag and drop handling
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('drag-over');
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('drag-over');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('drag-over');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleImageUpload(e.dataTransfer.files[0]);
        }
    });

    // Toggle camera flash
    cameraToggle.addEventListener('click', async () => {
        try {
            const track = video.srcObject?.getVideoTracks()[0];
            if (track?.getCapabilities().torch) {
                const torchState = !track.getConstraints().advanced?.[0]?.torch;
                await track.applyConstraints({
                    advanced: [{ torch: torchState }]
                });
                cameraToggle.textContent = torchState ? 'Flash Off' : 'Flash On';
            }
        } catch (err) {
            console.error('Failed to toggle flash:', err);
            cameraToggle.style.display = 'none';
        }
    });

    // Manual verification
    manualButton.addEventListener('click', () => {
        const applicationId = manualInput.value.trim();
        if (applicationId) {
            console.log('Manual verification for:', applicationId);
            handleScanResult(applicationId);
        } else {
            alert('Please enter a Gate Pass ID');
        }
    });

    // Handle scan result
    async function handleScanResult(result) {
        console.log('Processing scan result:', result);
        
        // Show loading state
        resultContainer.style.display = 'block';
        resultContainer.className = 'result-container loading';
        resultContainer.innerHTML = '<div class="result-title">Verifying...</div>';

        try {
            // Clean up the result - remove any URL parts if present
            const applicationId = result.split('/').pop().trim();
            console.log('Cleaned application ID:', applicationId);

            const response = await fetch(`/verify_api/?application_id=${encodeURIComponent(applicationId)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('API Data:', data);
            
            // Remove loading state
            resultContainer.classList.remove('loading');
            
            if (data.status === 'success') {
                resultContainer.className = 'result-container success';
                resultContainer.innerHTML = `
                    <div class="result-title">✅ Valid Gate Pass</div>
                    <div class="result-details">
                        <div class="result-label">Name:</div>
                        <div>${data.gatepass.first_name} ${data.gatepass.last_name}</div>
                        <div class="result-label">ID:</div>
                        <div>${data.gatepass.application_id}</div>
                        <div class="result-label">Department:</div>
                        <div>${data.gatepass.visiting_department}</div>
                        <div class="result-label">Valid Until:</div>
                        <div>${data.gatepass.valid_until}</div>
                    </div>
                `;

                // If in upload mode, show success state
                if (uploadMode.classList.contains('active')) {
                    uploadBox.classList.add('success');
                }
            } else {
                resultContainer.className = 'result-container error';
                resultContainer.innerHTML = `
                    <div class="result-title">❌ Invalid Gate Pass</div>
                    <div>${data.message || 'This gate pass is not valid.'}</div>
                `;

                // If in upload mode, show error state
                if (uploadMode.classList.contains('active')) {
                    uploadBox.classList.add('error');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            resultContainer.classList.remove('loading');
            resultContainer.className = 'result-container error';
            resultContainer.innerHTML = `
                <div class="result-title">❌ Error</div>
                <div>Failed to verify gate pass. Please try again.</div>
            `;

            // If in upload mode, show error state
            if (uploadMode.classList.contains('active')) {
                uploadBox.classList.add('error');
            }
        }
    }

    // Handle Enter key in manual input
    manualInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            manualButton.click();
        }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        stopScanner();
    });
}); 