// PQRS Form Handler

document.addEventListener('DOMContentLoaded', function() {
    const pqrsForm = document.getElementById('pqrsForm');
    const responseSection = document.getElementById('responseSection');
    const responseContent = document.getElementById('responseContent');
    const submitBtn = document.getElementById('submitBtn');

    if (pqrsForm) {
        pqrsForm.addEventListener('submit', handlePQRSSubmit);
    }

    async function handlePQRSSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(pqrsForm);
        const pqrsData = Utils.formDataToObject(formData);

        // Validation
        if (!validatePQRSData(pqrsData)) {
            return;
        }

        try {
            // Show loading
            Utils.showLoading('Procesando su PQRS...', 'Nuestro sistema de IA está analizando su solicitud');
            setSubmitButtonState(true);

            // Submit PQRS
            const response = await Utils.apiRequest('/pqrs/submit', {
                method: 'POST',
                body: JSON.stringify(pqrsData)
            });

            // Hide loading
            Utils.hideLoading();
            
            // Show response
            displayPQRSResponse(response);
            
            // Show success notification
            NotificationSystem.show(
                `PQRS enviada exitosamente. ID: ${response.pqrs_id}`,
                'success',
                8000
            );

            // Reset form
            pqrsForm.reset();

        } catch (error) {
            console.error('Error submitting PQRS:', error);
            Utils.hideLoading();
            
            NotificationSystem.show(
                'Error al enviar la PQRS. Por favor, intente nuevamente.',
                'danger'
            );
        } finally {
            setSubmitButtonState(false);
        }
    }

    function validatePQRSData(data) {
        const required = ['tipo', 'titulo', 'descripcion', 'ciudadano_nombre', 'ciudadano_email'];
        
        for (const field of required) {
            if (!data[field] || data[field].trim() === '') {
                NotificationSystem.show(
                    `El campo ${getFieldLabel(field)} es obligatorio.`,
                    'warning'
                );
                
                // Focus on the field
                const element = pqrsForm.querySelector(`[name="${field}"]`);
                if (element) {
                    element.focus();
                    element.classList.add('is-invalid');
                    setTimeout(() => element.classList.remove('is-invalid'), 3000);
                }
                
                return false;
            }
        }

        // Email validation
        if (data.ciudadano_email && !isValidEmail(data.ciudadano_email)) {
            NotificationSystem.show('Por favor ingrese un email válido.', 'warning');
            return false;
        }

        return true;
    }

    function getFieldLabel(field) {
        const labels = {
            'tipo': 'Tipo de PQRS',
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'ciudadano_nombre': 'Nombre completo',
            'ciudadano_email': 'Email'
        };
        return labels[field] || field;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function setSubmitButtonState(loading) {
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar PQRS';
        }
    }

    function displayPQRSResponse(response) {
        const confidenceColor = Utils.getConfidenceColor(response.confianza);
        const categoryName = Utils.formatCategoryName(response.categoria_detectada);
        
        const responseHtml = `
            <div class="pqrs-response">
                <!-- Header with ID and confidence -->
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6 class="text-primary mb-1">
                            <i class="fas fa-id-card me-2"></i>ID de PQRS
                        </h6>
                        <code class="fs-6">${response.pqrs_id}</code>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <h6 class="text-primary mb-1">
                            <i class="fas fa-chart-line me-2"></i>Confianza
                        </h6>
                        <div class="d-inline-block" style="width: 100px;">
                            <div class="confidence-meter">
                                <div class="confidence-fill" style="width: ${response.confianza * 100}%"></div>
                            </div>
                            <small class="text-${confidenceColor} fw-bold">
                                ${Utils.formatConfidence(response.confianza)}
                            </small>
                        </div>
                    </div>
                </div>

                <!-- Category and processing time -->
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6 class="text-primary mb-1">
                            <i class="fas fa-tag me-2"></i>Categoría Detectada
                        </h6>
                        <span class="category-badge">${categoryName}</span>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <h6 class="text-primary mb-1">
                            <i class="fas fa-clock me-2"></i>Tiempo de Respuesta
                        </h6>
                        <span class="text-muted">${response.tiempo_respuesta.toFixed(2)}s</span>
                    </div>
                </div>

                <!-- Main response -->
                <div class="mb-4">
                    <h6 class="text-primary mb-3">
                        <i class="fas fa-reply me-2"></i>Respuesta del Sistema
                    </h6>
                    <div class="bg-white p-4 rounded border">
                        ${formatResponseText(response.respuesta)}
                    </div>
                </div>

                <!-- Referenced documents -->
                ${response.documentos_referencia.length > 0 ? `
                    <div class="mb-4">
                        <h6 class="text-primary mb-3">
                            <i class="fas fa-file-alt me-2"></i>Documentos de Referencia
                        </h6>
                        <div class="row">
                            ${response.documentos_referencia.map(doc => `
                                <div class="col-md-6 mb-2">
                                    <div class="doc-reference">
                                        <small class="text-muted">
                                            <i class="fas fa-document me-1"></i>
                                            ${doc}
                                        </small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Recommendations -->
                ${response.recomendaciones.length > 0 ? `
                    <div class="mb-3">
                        <h6 class="text-primary mb-3">
                            <i class="fas fa-lightbulb me-2"></i>Recomendaciones
                        </h6>
                        <ul class="list-group list-group-flush">
                            ${response.recomendaciones.map(rec => `
                                <li class="list-group-item border-0 ps-0">
                                    <i class="fas fa-check text-success me-2"></i>
                                    ${rec}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                <!-- Action buttons -->
                <div class="text-center pt-3 border-top">
                    <button class="btn btn-outline-primary me-2" onclick="copyResponseToClipboard('${response.pqrs_id}')">
                        <i class="fas fa-copy me-2"></i>Copiar Respuesta
                    </button>
                    <button class="btn btn-outline-success me-2" onclick="downloadResponsePDF('${response.pqrs_id}')">
                        <i class="fas fa-download me-2"></i>Descargar PDF
                    </button>
                    <button class="btn btn-outline-info" onclick="shareResponse('${response.pqrs_id}')">
                        <i class="fas fa-share me-2"></i>Compartir
                    </button>
                </div>
            </div>
        `;

        responseContent.innerHTML = responseHtml;
        responseSection.style.display = 'block';
        responseSection.classList.add('success-animation');

        // Scroll to response
        setTimeout(() => {
            responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }

    function formatResponseText(text) {
        // Convert line breaks to HTML
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>');
    }
});

// Global functions for response actions
window.copyResponseToClipboard = function(pqrsId) {
    const responseElement = document.querySelector('#responseContent .bg-white');
    if (responseElement) {
        const text = responseElement.innerText;
        navigator.clipboard.writeText(`PQRS ID: ${pqrsId}\n\n${text}`)
            .then(() => {
                NotificationSystem.show('Respuesta copiada al portapapeles', 'success');
            })
            .catch(() => {
                NotificationSystem.show('Error al copiar al portapapeles', 'danger');
            });
    }
};

window.downloadResponsePDF = function(pqrsId) {
    // This would integrate with a PDF generation service
    NotificationSystem.show('Función de descarga PDF en desarrollo', 'info');
};

window.shareResponse = function(pqrsId) {
    if (navigator.share) {
        navigator.share({
            title: `PQRS ${pqrsId} - Respuesta`,
            text: 'Respuesta a PQRS de Infraestructura Medellín',
            url: window.location.href
        });
    } else {
        // Fallback: copy URL to clipboard
        navigator.clipboard.writeText(window.location.href)
            .then(() => {
                NotificationSystem.show('URL copiada al portapapeles', 'success');
            });
    }
};