/* NEXUS Uploader Engine v2 — Direct API Upload */
document.addEventListener('DOMContentLoaded', function () {
    const dropzone  = document.getElementById('nexus-dropzone');
    const fileInput = document.getElementById('nexus-upload-input');
    const statusText= document.getElementById('nexus-status-text');
    const progressBar   = document.getElementById('nexus-progress-bar');
    const progressInner = document.getElementById('nexus-progress-inner');
    const hiddenPath= document.getElementById('nexus-file-path-hidden');

    if (!dropzone) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#00d2ff';
    });
    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = '#0073aa';
    });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#0073aa';
        handleFiles(e.dataTransfer.files);
    });
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

    function handleFiles(files) {
        if (!files || files.length === 0) return;
        const file = files[0];
        statusText.innerText = `Подготовка: ${file.name}`;
        progressBar.style.display = 'block';
        progressInner.style.width = '0%';
        uploadFile(file);
    }

    function uploadFile(file) {
        const endpoint = nexus_config.endpoint + '/api/upload';
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', endpoint, true);

        // Обход предупреждения Ngrok
        xhr.setRequestHeader('ngrok-skip-browser-warning', 'true');

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                progressInner.style.width = pct + '%';
                statusText.innerText = `Загрузка: ${pct}%`;
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                const res = JSON.parse(xhr.responseText);
                hiddenPath.value = res.key;
                progressInner.style.width = '100%';
                statusText.innerText = `✅ Загружено: ${file.name}`;
                console.log('NEXUS upload OK:', res.key);
            } else {
                statusText.innerText = `❌ Ошибка: ${xhr.statusText}`;
                console.error('NEXUS upload failed:', xhr.responseText);
            }
        };

        xhr.onerror = () => {
            statusText.innerText = `❌ Ошибка сети. Проверьте туннель.`;
            console.error('NEXUS network error');
        };

        xhr.send(formData);
    }
});
