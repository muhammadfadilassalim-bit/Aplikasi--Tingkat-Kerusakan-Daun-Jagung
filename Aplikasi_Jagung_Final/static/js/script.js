const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const previewImg = document.getElementById('preview-img');
        const captureBtn = document.getElementById('capture-btn');
        const uploadScanBtn = document.getElementById('upload-scan-btn');
        const scannerLine = document.getElementById('scanner-line');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        let currentMode = 'camera';
        let isFrozen = false;
        let savedBlob = null;

        function switchMode(mode) {
            currentMode = mode;
            if (mode === 'camera') {
                document.getElementById('tab-cam-btn').className = 'tab-btn tab-active';
                document.getElementById('tab-upload-btn').className = 'tab-btn tab-inactive';
                document.getElementById('camera-controls').classList.remove('hidden');
                document.getElementById('upload-controls').classList.add('hidden');
                previewImg.classList.add('hidden');
                video.classList.remove('hidden');
                statusText.innerText = "Kamera Nonaktif";
                statusDot.style.backgroundColor = "#f43f5e";
            } else {
                document.getElementById('tab-upload-btn').className = 'tab-btn tab-active';
                document.getElementById('tab-cam-btn').className = 'tab-btn tab-inactive';
                document.getElementById('upload-controls').classList.remove('hidden');
                document.getElementById('camera-controls').classList.add('hidden');
                video.classList.add('hidden');
                canvas.classList.add('hidden');
                previewImg.classList.remove('hidden');
                statusText.innerText = "Mode Upload File";
                statusDot.style.backgroundColor = "#3b82f6";
            }
        }

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                video.srcObject = stream;
                
                captureBtn.disabled = false;
                statusDot.style.backgroundColor = "#10b981";
                statusText.innerText = "Kamera Aktif";
                document.getElementById('start-btn').innerText = "✓ Kamera Terhubung";
                document.getElementById('start-btn').disabled = true;
                document.getElementById('start-btn').style.opacity = "0.6";
            } catch (err) {
                alert("Gagal membuka akses kamera: " + err.message);
            }
        }

        function takeSnapshot() {
            if (!isFrozen) {
                const context = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                video.classList.add('hidden');
                canvas.classList.remove('hidden');
                
                canvas.toBlob((blob) => {
                    savedBlob = blob;
                    isFrozen = true;
                    captureBtn.innerText = "🔍 Analisis Hasil Potret";
                    captureBtn.className = "btn-scan";
                    statusText.innerText = "Gambar Terkunci";
                    statusDot.style.backgroundColor = "#f59e0b";
                }, 'image/jpeg', 0.90);

            } else {
                sendToYOLO();
            }
        }

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                savedBlob = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    uploadScanBtn.disabled = false;
                    statusText.innerText = "File Siap Didekstrasi";
                    statusDot.style.backgroundColor = "#10b981";
                }
                reader.readAsDataURL(file);
            }
        }

        async function sendToYOLO() {
            if (!savedBlob) return;

            const formData = new FormData();
            formData.append('file', savedBlob, 'daun_jagung_sample.jpg');

            scannerLine.classList.add('scan-active');

            document.getElementById('result-container').innerHTML = `
                <div style="padding: 40px 16px; text-align: center; background-color: white; border: 1px solid #e2e8f0; border-radius: 16px;">
                    <div style="font-weight: 700; color: #334155; font-size: 16px;">Model YOLOv11 + HSV Sedang Menganalisis...</div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Menghitung persentase piksel luas area kerusakan daun</div>
                </div>
            `;

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'ngrok-skip-browser-warning': 'true'
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP Error Status: ${response.status}`);
                }

                const htmlResult = await response.text();
                document.getElementById('result-container').innerHTML = htmlResult;

                scannerLine.classList.remove('scan-active');
                
                if (currentMode === 'camera') {
                    captureBtn.innerText = "🔄 Ambil Foto Ulang";
                    captureBtn.className = "btn-reset";
                    captureBtn.setAttribute("onclick", "resetCamera()");
                }
            } catch (err) {
                scannerLine.classList.remove('scan-active');
                document.getElementById('result-container').innerHTML = `
                    <div style="padding: 16px; background-color: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; border-radius: 12px; text-align: center;">
                        <strong>❌ Gagal Menganalisis Gambar</strong>
                        <p style="font-size: 12px; margin-top: 4px;">${err.message}</p>
                    </div>
                `;
            }
        }

        function resetCamera() {
            isFrozen = false;
            savedBlob = null;
            
            canvas.classList.add('hidden');
            video.classList.remove('hidden');
            
            captureBtn.innerText = "📸 Potret Gambar Daun";
            captureBtn.className = "btn-primary";
            captureBtn.setAttribute("onclick", "takeSnapshot()");
            
            statusText.innerText = "Kamera Aktif";
            statusDot.style.backgroundColor = "#10b981";
        }
