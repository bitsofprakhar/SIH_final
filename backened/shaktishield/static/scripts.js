const API_BASE = window.location.origin;
let currentBatchJob = null;

// Check API and model status on page load
window.onload = function() {
    checkApiStatus();
    checkModelStatus();
    setupFileInputs();
};

function generateVariations() {
    const file = document.getElementById('variationFile').files[0];
    const count = document.getElementById('variationCount').value;

    if (!file) {
        showAlert('danger', 'Please select an original document.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('count', count);

    showResults('variationResults', '<div class="loading"></div> Generating variations...');

    fetch(`${API_BASE}/generate/variations`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResults('variationResults', `
                <div class="alert alert-success">
                    <strong>✅ Variations Generated Successfully!</strong><br>
                    Generated: ${data.variations_generated} variations<br>
                    Original: ${data.original_filename}<br>
                    Job ID: ${data.job_id}<br>
                    <strong>Augmentation methods used:</strong>
                    <ul>
                        ${data.details.augmentation_methods_used.map(method => `<li>${method}</li>`).join('')}
                    </ul>
                </div>
            `);
        } else {
            showResults('variationResults', `<div class="alert alert-danger">❌ Variation generation failed: ${data.error}</div>`);
        }
    })
    .catch(error => {
        showResults('variationResults', `<div class="alert alert-danger">❌ Variation generation error: ${error.message}</div>`);
    });
}


//function verifySingle() {
//    const file = document.getElementById('singleFile').files[0];
//
//    if (!file) {
//        showAlert('danger', 'Please select a document to verify.');
//        return;
//    }
//
//    const formData = new FormData();
//    formData.append('file', file);
//
//    showResults('singleResults', '<div class="loading"></div> Analyzing document...');
//
//    fetch(`${API_BASE}/verify/single`, {
//        method: 'POST',
//        body: formData
//    })
//    .then(response => response.json())
//    .then(data => {
//        if (data.status === 'success') {
//            const result = data.verification_result;
//            const isAuthentic = result.document_status === 'AUTHENTIC';
//
//            showResults('singleResults', `
//                <div class="result-item ${isAuthentic ? 'result-authentic' : 'result-suspicious'}">
//                    <h4>${isAuthentic ? '✅' : '❌'} ${result.document_status}</h4>
//                    <p><strong>Confidence:</strong> ${result.confidence_score}</p>
//                    <p><strong>Recommendation:</strong> ${result.recommendation}</p>
//                    <details style="margin-top: 10px;">
//                        <summary>Detailed Analysis</summary>
//                        <ul>
//                            <li>Random Forest: ${result.detailed_analysis.random_forest_confidence}</li>
//                            <li>CNN: ${result.detailed_analysis.cnn_confidence}</li>
//                            <li>Combined: ${result.detailed_analysis.combined_confidence}</li>
//                        </ul>
//                    </details>
//                </div>
//            `);
//        } else {
//            showResults('singleResults', `<div class="alert alert-danger">❌ Verification failed: ${data.error}</div>`);
//        }
//    })
//    .catch(error => {
//        showResults('singleResults', `<div class="alert alert-danger">❌ Verification error: ${error.message}</div>`);
//    });
//}
function verifySingle() {
    const file = document.getElementById('singleFile').files[0];

    if (!file) {
        showAlert('danger', 'Please select a document to verify.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showResults('singleResults', '<div class="loading"></div> Analyzing document with OCR and database validation...');

    fetch(`${API_BASE}/verify/enhanced`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'completed') {
            const isAuthentic = data.final_verdict === 'AUTHENTIC';

            showResults('singleResults', `
                <div class="result-item ${isAuthentic ? 'result-authentic' : 'result-suspicious'}">
                    <h4>${isAuthentic ? '✅' : '❌'} ${data.final_verdict}</h4>
                    <p><strong>Combined Confidence:</strong> ${data.combined_confidence || 'N/A'}</p>
                    <p><strong>Recommendation:</strong> ${data.recommendation}</p>

                    <details style="margin-top: 10px;">
                        <summary>OCR Extraction</summary>
                        <ul>
                            <li>MS No: ${data.steps.ocr_extraction?.extracted_data?.ms_no || 'Not found'}</li>
                            <li>Name: ${data.steps.ocr_extraction?.extracted_data?.name || 'Not found'}</li>
                            <li>College: ${data.steps.ocr_extraction?.extracted_data?.college || 'Not found'}</li>
                            <li>Total Marks: ${data.steps.ocr_extraction?.extracted_data?.total_marks || 'Not found'}</li>
                        </ul>
                    </details>

                    <details style="margin-top: 10px;">
                        <summary>Database Validation</summary>
                        <ul>
                            <li>Valid: ${data.steps.database_validation?.is_valid ? 'Yes' : 'No'}</li>
                            <li>Confidence: ${(data.steps.database_validation?.confidence * 100).toFixed(1)}%</li>
                        </ul>
                    </details>

                    <details style="margin-top: 10px;">
                        <summary>ML Analysis</summary>
                        <ul>
                            <li>Authentic: ${data.steps.ml_authenticity?.is_authentic ? 'Yes' : 'No'}</li>
                            <li>RF Confidence: ${(data.steps.ml_authenticity?.rf_confidence * 100).toFixed(1)}%</li>
                            <li>CNN Confidence: ${(data.steps.ml_authenticity?.cnn_confidence * 100).toFixed(1)}%</li>
                        </ul>
                    </details>
                </div>
            `);
        } else if (data.status === 'invalid') {
            showResults('singleResults', `<div class="alert alert-danger">❌ ${data.final_verdict}: ${data.recommendation}</div>`);
        } else {
            showResults('singleResults', `<div class="alert alert-danger">❌ Verification failed: ${data.error}</div>`);
        }
    })
    .catch(error => {
        showResults('singleResults', `<div class="alert alert-danger">❌ Verification error: ${error.message}</div>`);
    });
}


// Add at the global (top) level, outside all other functions:

function showResults(elementId, html) {
    document.getElementById(elementId).innerHTML = html;
}

function showAlert(type, message) {
    const alertHtml = `<div class="alert alert-${type}">${message}</div>`;
    console.log(alertHtml); // Optionally show messages globally
}

function showTab(tabName, event) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Highlight the clicked button
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}


function startTraining() {
    // Your implementation goes here.
    // Example logic:
    const files = document.getElementById('trainFiles').files;
    const variations = document.getElementById('variationsCount').value;

    if (files.length === 0) {
        showAlert('danger', 'Please select original documents to upload.');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    formData.append('variations_per_image', variations);

    showResults('trainingResults', '<div class="loading"></div> Training in progress... This may take several minutes.');

    fetch(`${API_BASE}/train`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResults('trainingResults', `
                <div class="alert alert-success">
                    <strong>✅ Training Completed Successfully!</strong>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${data.training_results.total_samples}</div>
                            <div class="stat-label">Training Samples</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.training_results.rf_accuracy}</div>
                            <div class="stat-label">Random Forest Accuracy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.training_results.cnn_accuracy}</div>
                            <div class="stat-label">CNN Accuracy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.training_results.original_documents_used}</div>
                            <div class="stat-label">Original Documents</div>
                        </div>
                    </div>
                </div>
            `);
            checkModelStatus(); // Update model status
        } else {
            showResults('trainingResults', `<div class="alert alert-danger">❌ Training failed: ${data.error}</div>`);
        }
    })
    .catch(error => {
        showResults('trainingResults', `<div class="alert alert-danger">❌ Training error: ${error.message}</div>`);
    });
}

//function checkApiStatus() {
//    fetch(`${API_BASE}/health`)
//        .then(response => response.json())
//        .then(data => {
//            const statusEl = document.getElementById('apiStatus');
//            if (data.status === 'healthy') {
//                statusEl.className = 'status-indicator status-online';
//                statusEl.textContent = 'API: Online';
//            } else {
//                throw new Error('API unhealthy');
//            }
//        })
//        .catch(error => {
//            const statusEl = document.getElementById('apiStatus');
//            statusEl.className = 'status-indicator status-offline';
//            statusEl.textContent = 'API: Offline';
//        });
//}
function checkApiStatus() {
  console.log('API Status: Online (Django Backend)');
  // Skip API status check for now as we don't have the health endpoint
}

function setStatus(isOnline, elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = isOnline ? 'Online' : 'Offline';
    element.className = isOnline ? 'status-online' : 'status-offline';
  }
}

//function checkModelStatus() {
//    fetch(`${API_BASE}/model/status`)
//        .then(response => response.json())
//        .then(data => {
//            const statusEl = document.getElementById('modelStatus');
//            if (data.model_trained) {
//                statusEl.className = 'status-indicator status-online';
//                statusEl.textContent = 'Model: Trained & Ready';
//            } else if (data.models_initialized) {
//                statusEl.className = 'status-indicator status-training';
//                statusEl.textContent = 'Model: Needs Training';
//            } else {
//                statusEl.className = 'status-indicator status-offline';
//                statusEl.textContent = 'Model: Not Loaded';
//            }
//        })
//        .catch(error => {
//            const statusEl = document.getElementById('modelStatus');
//            statusEl.className = 'status-indicator status-offline';
//            statusEl.textContent = 'Model: Error';
//        });
//}
function checkModelStatus() {
  console.log('Model Status: Training Mode (Demo)');
  // Skip model status check for now as we don't have the model/status endpoint
}



function setupFileInputs() {
    // Setup drag and drop for all file input areas
    const fileAreas = document.querySelectorAll('.file-input-area');
    fileAreas.forEach(area => {
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            const files = e.dataTransfer.files;
            // Corrected regex: closed the capture group properly
            const match = area.getAttribute('onclick').match(/getElementById\('([^']+)'\)/);
            if (match) {
                const inputId = match[1];
                const input = document.getElementById(inputId);
                if (input) {
                    input.files = files;
                    updateFileList(inputId);
                }
            }
        });
    });

    // Setup file input change listeners
    document.getElementById('trainFiles').addEventListener('change', () => updateFileList('trainFiles'));
    document.getElementById('singleFile').addEventListener('change', () => updateFileList('singleFile'));
    document.getElementById('batchFiles').addEventListener('change', () => updateFileList('batchFiles'));
    document.getElementById('variationFile').addEventListener('change', () => updateFileList('variationFile'));
}

function updateFileList(inputId) {
    const input = document.getElementById(inputId);
    const files = input.files;
    let listElementId;

    switch(inputId) {
        case 'trainFiles': listElementId = 'trainFileList'; break;
        case 'singleFile': listElementId = 'singleFileInfo'; break;
        case 'batchFiles': listElementId = 'batchFileList'; break;
        case 'variationFile': listElementId = 'variationFileInfo'; break;
        default: listElementId = null;
    }

    if (!listElementId) return;

    const listElement = document.getElementById(listElementId);
    if (files.length > 0) {
        let html = '<strong>Selected files:</strong><ul>';
        for (let i = 0; i < files.length; i++) {
            html += `<li>${files[i].name} (${(files[i].size / 1024 / 1024).toFixed(2)} MB)</li>`;
        }
        html += '</ul>';
        listElement.innerHTML = html;
    } else {
        listElement.innerHTML = '';
    }
}

// Make sure `event` parameter is declared for inline onclick handlers
function showTab(tabName, event) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}
//batch verify
function batchVerify() {
    const files = document.getElementById('batchFiles').files;
    if (!files || files.length === 0) {
        showAlert('danger', 'Please select files for batch verification.');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    showResults('batchResults', 'Processing batch verification...');

    fetch(`${API_BASE}/verify_batch`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            displayBatchResults(data.results);
        } else {
            showAlert('danger', `Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Network error occurred.');
    });
}

//newly added
function displayBatchResults(results) {
    let resultHtml = '<h4>Batch Verification Results:</h4>';
    results.forEach((result, index) => {
        resultHtml += `
            <div class="result-item">
                <strong>File:</strong> ${result.filename}<br>
                <strong>Status:</strong> ${result.status}<br>
                ${result.is_authentic !== undefined ?
                    `<strong>Authentic:</strong> ${result.is_authentic ? 'Yes' : 'No'}<br>
                     <strong>Confidence:</strong> ${result.confidence}<br>` : ''}
                ${result.error ? `<strong>Error:</strong> ${result.error}<br>` : ''}
            </div><hr>
        `;
    });
    showResults('batchResults', resultHtml);
}


// Keep all other functions as-is from your code...

// Make sure to update your HTML button handlers to pass the event object:
// Example: <button onclick="showTab('train', event)">Train Model</button>

