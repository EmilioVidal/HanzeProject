// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const previewSection = document.getElementById('previewSection');
const loadingSection = document.getElementById('loadingSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const previewImage = document.getElementById('previewImage');
const resultImage = document.getElementById('resultImage');
const processBtn = document.getElementById('processBtn');
const cancelBtn = document.getElementById('cancelBtn');
const uploadAnotherBtn = document.getElementById('uploadAnotherBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');

const objectCount = document.getElementById('objectCount');
const totalArea = document.getElementById('totalArea');
const avgArea = document.getElementById('avgArea');
const objectList = document.getElementById('objectList');
const errorText = document.getElementById('errorText');

let selectedFile = null;

// File upload handlers
uploadBox.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

// Drag and drop handlers
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    handleFileSelect(e.dataTransfer.files[0]);
});

// Handle file selection
function handleFileSelect(file) {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file.');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        showSection('preview');
    };
    reader.readAsDataURL(file);
}

// Process image
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    showSection('loading');

    const formData = new FormData();
    formData.append('file', selectedFile);


    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Display results
        displayResults(data);

    } catch (error) {
        showError('An error occurred while processing the image. Please try again.');
        console.error('Error:', error);
    }
});

// Display results
function displayResults(data) {
    objectCount.textContent = data.object_count;
    totalArea.textContent = Math.round(data.total_area).toLocaleString();
    avgArea.textContent = data.object_count > 0
        ? Math.round(data.total_area / data.object_count).toLocaleString()
        : 0;

    resultImage.src = data.result_image;

    // Display object list
    objectList.innerHTML = '<h3 style="margin-bottom: 15px;">Individual Objects:</h3>';
    data.object_sizes.forEach((size, index) => {
        const item = document.createElement('div');
        item.className = 'object-item';
        item.innerHTML = `
            <span class="object-number">Object ${index + 1}</span>
            <span class="object-area">${Math.round(size).toLocaleString()} px²</span>
        `;
        objectList.appendChild(item);
    });

    showSection('result');
}

// Show error
function showError(message) {
    errorText.textContent = message;
    showSection('error');
}

// Reset to upload
function resetToUpload() {
    selectedFile = null;
    fileInput.value = '';
    showSection('upload');
}

// Section visibility control
function showSection(section) {
    uploadSection.style.display = 'none';
    previewSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';

    switch (section) {
        case 'upload':
            uploadSection.style.display = 'block';
            break;
        case 'preview':
            previewSection.style.display = 'block';
            break;
        case 'loading':
            loadingSection.style.display = 'block';
            break;
        case 'result':
            resultSection.style.display = 'block';
            break;
        case 'error':
            errorSection.style.display = 'block';
            break;
    }
}

// Button handlers
cancelBtn.addEventListener('click', resetToUpload);
uploadAnotherBtn.addEventListener('click', resetToUpload);
tryAgainBtn.addEventListener('click', resetToUpload);
