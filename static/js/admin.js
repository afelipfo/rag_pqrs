// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize admin panel
    initializeAdminPanel();
    
    // Load initial stats
    refreshStats();
    
    // Set up event listeners
    setupEventListeners();
});

function initializeAdminPanel() {
    // Load categories for upload and search forms
    CategoryManager.loadCategories().then(() => {
        const uploadCategoria = document.getElementById('uploadCategoria');
        const searchCategoria = document.getElementById('searchCategoria');
        
        if (uploadCategoria) {
            CategoryManager.populateSelect(uploadCategoria);
        }
        
        if (searchCategoria) {
            CategoryManager.populateSelect(searchCategoria, true);
        }
    });
}

function setupEventListeners() {
    // Upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }

    // Search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleDocumentSearch);
    }

    // File input change
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileInputChange);
    }
}

async function handleFileUpload(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const file = formData.get('file');
    
    if (!file || file.size === 0) {
        NotificationSystem.show('Por favor seleccione un archivo', 'warning');
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        NotificationSystem.show('El archivo es demasiado grande. Máximo 10MB.', 'warning');
        return;
    }

    try {
        showAdminLoading('Subiendo documento...', 'Procesando archivo y generando embeddings');

        const response = await fetch('/api/v1/documents/upload', {
            method: 'POST',
            body: formData
        });

        hideAdminLoading();

        if (response.ok) {
            const result = await response.json();
            
            NotificationSystem.show(
                `Documento "${result.titulo}" subido exitosamente`,
                'success'
            );

            // Show upload results
            showUploadResults(result);
            
            // Reset form
            event.target.reset();
            
            // Refresh stats
            refreshStats();
            
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error subiendo archivo');
        }

    } catch (error) {
        hideAdminLoading();
        console.error('Upload error:', error);
        NotificationSystem.show(
            `Error subiendo archivo: ${error.message}`,
            'danger'
        );
    }
}

async function handleDocumentSearch(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const query = formData.get('query');
    const categoria = formData.get('categoria');
    const limit = parseInt(formData.get('limit')) || 10;

    if (!query.trim()) {
        NotificationSystem.show('Por favor ingrese una consulta', 'warning');
        return;
    }

    try {
        showAdminLoading('Buscando documentos...', 'Realizando búsqueda vectorial');

        const params = new URLSearchParams({
            query: query,
            limit: limit.toString()
        });

        if (categoria) {
            params.append('categoria', categoria);
        }

        const response = await Utils.apiRequest(`/documents/search?${params}`);
        
        hideAdminLoading();
        
        displaySearchResults(response);

    } catch (error) {
        hideAdminLoading();
        console.error('Search error:', error);
        NotificationSystem.show('Error en la búsqueda', 'danger');
    }
}

function handleFileInputChange(event) {
    const file = event.target.files[0];
    const titleInput = document.querySelector('[name="titulo"]');
    
    if (file && !titleInput.value) {
        // Auto-fill title with filename (without extension)
        const filename = file.name.replace(/\.[^/.]+$/, "");
        titleInput.value = filename;
    }
}

function showUploadResults(result) {
    const uploadResults = document.getElementById('uploadResults');
    const uploadMessage = document.getElementById('uploadMessage');
    
    if (uploadResults && uploadMessage) {
        uploadMessage.textContent = `Documento "${result.titulo}" procesado correctamente`;
        uploadResults.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            uploadResults.style.display = 'none';
        }, 5000);
    }
}

function displaySearchResults(response) {
    const searchResults = document.getElementById('searchResults');
    const searchResultsContent = document.getElementById('searchResultsContent');
    
    if (!searchResults || !searchResultsContent) return;

    if (response.resultados === 0) {
        searchResultsContent.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No se encontraron resultados</h5>
                <p class="text-muted">Intenta con otros términos de búsqueda</p>
            </div>
        `;
    } else {
        const resultsHtml = `
            <div class="mb-3">
                <h6 class="text-primary">
                    <i class="fas fa-search me-2"></i>
                    ${response.resultados} resultado(s) para: "${response.query}"
                </h6>
            </div>
            
            <div class="search-results-list">
                ${response.documentos.map((doc, index) => `
                    <div class="search-result-item mb-3">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-1">
                                <i class="fas fa-file-alt text-primary me-2"></i>
                                ${doc.metadata.titulo}
                            </h6>
                            <span class="similarity-badge">
                                ${Math.round(doc.similitud * 100)}%
                            </span>
                        </div>
                        
                        <div class="mb-2">
                            <span class="badge bg-secondary me-2">
                                ${Utils.formatCategoryName(doc.metadata.categoria)}
                            </span>
                            <small class="text-muted">
                                <i class="fas fa-calendar me-1"></i>
                                ${Utils.formatDate(doc.metadata.fecha_creacion)}
                            </small>
                        </div>
                        
                        <div class="document-content">
                            <p class="small mb-0">
                                ${truncateText(doc.documento, 200)}
                            </p>
                        </div>
                        
                        <div class="mt-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="expandDocument(${index})">
                                <i class="fas fa-expand me-1"></i>Ver más
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        searchResultsContent.innerHTML = resultsHtml;
    }
    
    searchResults.style.display = 'block';
    searchResults.scrollIntoView({ behavior: 'smooth' });
}

async function refreshStats() {
    try {
        const response = await Utils.apiRequest('/health');
        
        // Update stats cards
        updateStatsCard('totalDocs', response.vector_store.total_documentos);
        updateStatsCard('systemStatus', response.vector_store.status);
        
        // Update detailed stats
        updateDetailedStats(response);
        
    } catch (error) {
        console.error('Error refreshing stats:', error);
        updateStatsCard('systemStatus', 'Error');
    }
}

function updateStatsCard(cardId, value) {
    const element = document.getElementById(cardId);
    if (element) {
        if (cardId === 'systemStatus') {
            element.textContent = value === 'activo' ? 'Activo' : 
                                 value === 'vacío' ? 'Vacío' : 'Error';
        } else {
            element.textContent = value;
        }
    }
}

function updateDetailedStats(data) {
    const detailedStats = document.getElementById('detailedStats');
    if (!detailedStats) return;

    const statsHtml = `
        <div class="row">
            <div class="col-12 mb-3">
                <h6 class="text-primary">
                    <i class="fas fa-database me-2"></i>Base de Datos Vectorial
                </h6>
                <ul class="list-unstyled small">
                    <li><strong>Total documentos:</strong> ${data.vector_store.total_documentos}</li>
                    <li><strong>Estado:</strong> <span class="badge bg-${getStatusColor(data.vector_store.status)}">${data.vector_store.status}</span></li>
                </ul>
            </div>
            
            <div class="col-12 mb-3">
                <h6 class="text-primary">
                    <i class="fas fa-cog me-2"></i>Sistema
                </h6>
                <ul class="list-unstyled small">
                    <li><strong>Estado general:</strong> <span class="badge bg-${data.status === 'ok' ? 'success' : 'danger'}">${data.status}</span></li>
                    <li><strong>Última actualización:</strong> ${new Date().toLocaleString('es-CO')}</li>
                </ul>
            </div>
        </div>
    `;
    
    detailedStats.innerHTML = statsHtml;
}

function getStatusColor(status) {
    switch(status) {
        case 'activo': return 'success';
        case 'vacío': return 'warning';
        case 'error': return 'danger';
        default: return 'secondary';
    }
}

function confirmClearDatabase() {
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    confirmModal.show();
}

async function clearDatabase() {
    try {
        showAdminLoading('Limpiando base de datos...', 'Esta operación puede tomar unos momentos');
        
        const response = await Utils.apiRequest('/documents/clear', {
            method: 'DELETE'
        });
        
        hideAdminLoading();
        
        NotificationSystem.show(response.mensaje, 'success');
        
        // Hide confirmation modal
        const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
        confirmModal.hide();
        
        // Refresh stats
        refreshStats();
        
    } catch (error) {
        hideAdminLoading();
        console.error('Error clearing database:', error);
        NotificationSystem.show('Error limpiando la base de datos', 'danger');
    }
}

function exportData() {
    NotificationSystem.show('Función de exportación en desarrollo', 'info');
}

function showAdminLoading(title, subtitle) {
    const modal = document.getElementById('adminLoadingModal');
    const loadingText = document.getElementById('loadingText');
    const loadingSubtext = document.getElementById('loadingSubtext');
    
    if (modal && loadingText && loadingSubtext) {
        loadingText.textContent = title;
        loadingSubtext.textContent = subtitle;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

function hideAdminLoading() {
    const modal = document.getElementById('adminLoadingModal');
    if (modal) {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    }
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function expandDocument(index) {
    // This would show a modal with the full document content
    NotificationSystem.show('Función de expandir documento en desarrollo', 'info');
}

// Global functions
window.refreshStats = refreshStats;
window.clearDatabase = clearDatabase;
window.confirmClearDatabase = confirmClearDatabase;
window.exportData = exportData;
window.expandDocument = expandDocument;