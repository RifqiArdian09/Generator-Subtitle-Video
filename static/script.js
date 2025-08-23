class SubtitleGenerator {
    constructor() {
        this.currentTaskId = null;
        this.selectedFile = null;
        this.statusCheckInterval = null;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.videoInput = document.getElementById('videoInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.selectedFileDiv = document.getElementById('selectedFile');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.removeFileBtn = document.getElementById('removeFile');
        this.processBtn = document.getElementById('processBtn');
        
        // Section elements
        this.uploadSection = document.getElementById('uploadSection');
        this.processingSection = document.getElementById('processingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        // Processing elements
        this.processingStatus = document.getElementById('processingStatus');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.steps = {
            step1: document.getElementById('step1'),
            step2: document.getElementById('step2'),
            step3: document.getElementById('step3'),
            step4: document.getElementById('step4')
        };
        
        // Results elements
        this.subtitlePreview = document.getElementById('subtitlePreview');
        this.downloadSRT = document.getElementById('downloadSRT');
        this.downloadVTT = document.getElementById('downloadVTT');
        this.processAnother = document.getElementById('processAnother');
        
        // Error elements
        this.errorMessage = document.getElementById('errorMessage');
        this.retryBtn = document.getElementById('retryBtn');
        
        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }
    
    bindEvents() {
        // Upload events
        this.uploadArea.addEventListener('click', () => this.videoInput.click());
        this.uploadBtn.addEventListener('click', () => this.videoInput.click());
        this.videoInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // File management events
        this.removeFileBtn.addEventListener('click', () => this.removeFile());
        this.processBtn.addEventListener('click', () => this.processVideo());
        
        // Results events
        this.downloadSRT.addEventListener('click', () => this.downloadSubtitle('srt'));
        this.downloadVTT.addEventListener('click', () => this.downloadSubtitle('vtt'));
        this.processAnother.addEventListener('click', () => this.resetToUpload());
        
        // Error events
        this.retryBtn.addEventListener('click', () => this.resetToUpload());
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }
    
    handleFile(file) {
        // Validate file type
        const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo', 'video/x-ms-wmv'];
        const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv'];
        
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            this.showError('Format file tidak didukung. Gunakan: MP4, AVI, MOV, MKV, atau WMV');
            return;
        }
        
        // Validate file size (500MB)
        const maxSize = 500 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('Ukuran file terlalu besar. Maksimal 500MB');
            return;
        }
        
        this.selectedFile = file;
        this.displaySelectedFile();
    }
    
    displaySelectedFile() {
        this.fileName.textContent = this.selectedFile.name;
        this.fileSize.textContent = this.formatFileSize(this.selectedFile.size);
        
        this.uploadArea.style.display = 'none';
        this.selectedFileDiv.style.display = 'block';
    }
    
    removeFile() {
        this.selectedFile = null;
        this.videoInput.value = '';
        
        this.uploadArea.style.display = 'block';
        this.selectedFileDiv.style.display = 'none';
    }
    
    async processVideo() {
        if (!this.selectedFile) {
            this.showError('Pilih file video terlebih dahulu');
            return;
        }
        
        this.showLoading(true);
        
        try {
            // Upload video
            const formData = new FormData();
            formData.append('video', this.selectedFile);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Gagal mengupload video');
            }
            
            this.currentTaskId = result.task_id;
            this.showProcessingSection();
            this.startStatusCheck();
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    startStatusCheck() {
        this.statusCheckInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.currentTaskId}`);
                const status = await response.json();
                
                this.updateProcessingStatus(status);
                
                if (status.status === 'completed') {
                    clearInterval(this.statusCheckInterval);
                    await this.loadResults();
                } else if (status.status === 'error') {
                    clearInterval(this.statusCheckInterval);
                    this.showError(status.error || 'Terjadi kesalahan saat memproses video');
                }
                
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }, 2000);
    }
    
    updateProcessingStatus(status) {
        const progress = status.progress || 0;
        
        // Update progress bar
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `${progress}%`;
        
        // Update status text and steps
        if (progress < 20) {
            this.processingStatus.textContent = 'Mengekstrak audio dari video...';
            this.setActiveStep('step1');
        } else if (progress < 50) {
            this.processingStatus.textContent = 'Menganalisis audio dan mendeteksi suara...';
            this.setActiveStep('step2');
        } else if (progress < 80) {
            this.processingStatus.textContent = 'Menggenerate subtitle dari audio...';
            this.setActiveStep('step3');
        } else {
            this.processingStatus.textContent = 'Menyinkronkan subtitle dengan video...';
            this.setActiveStep('step4');
        }
    }
    
    setActiveStep(activeStepId) {
        Object.keys(this.steps).forEach(stepId => {
            this.steps[stepId].classList.remove('active');
        });
        this.steps[activeStepId].classList.add('active');
    }
    
    async loadResults() {
        try {
            const response = await fetch(`/preview/${this.currentTaskId}`);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Gagal memuat hasil');
            }
            
            this.displaySubtitles(result.subtitles);
            this.showResultsSection();
            
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    displaySubtitles(subtitles) {
        this.subtitlePreview.innerHTML = '';
        
        if (!subtitles || subtitles.length === 0) {
            this.subtitlePreview.innerHTML = '<p>Tidak ada subtitle yang berhasil digenerate.</p>';
            return;
        }
        
        subtitles.forEach((subtitle, index) => {
            const subtitleItem = document.createElement('div');
            subtitleItem.className = 'subtitle-item';
            
            const timeRange = `${this.formatTime(subtitle.start)} --> ${this.formatTime(subtitle.end)}`;
            
            subtitleItem.innerHTML = `
                <div class="subtitle-time">${timeRange}</div>
                <div class="subtitle-text">${subtitle.text}</div>
            `;
            
            this.subtitlePreview.appendChild(subtitleItem);
        });
    }
    
    async downloadSubtitle(format) {
        if (!this.currentTaskId) {
            this.showError('Tidak ada subtitle untuk didownload');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await fetch(`/export/${this.currentTaskId}/${format}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Gagal mendownload subtitle');
            }
            
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `subtitles.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    showProcessingSection() {
        this.hideAllSections();
        this.processingSection.style.display = 'block';
    }
    
    showResultsSection() {
        this.hideAllSections();
        this.resultsSection.style.display = 'block';
    }
    
    showError(message) {
        this.hideAllSections();
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
    }
    
    resetToUpload() {
        this.hideAllSections();
        this.uploadSection.style.display = 'block';
        this.removeFile();
        
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        
        this.currentTaskId = null;
    }
    
    hideAllSections() {
        this.uploadSection.style.display = 'none';
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }
    
    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SubtitleGenerator();
});

// Handle page visibility changes to pause/resume status checking
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, you might want to reduce polling frequency
        console.log('Page hidden - consider reducing polling frequency');
    } else {
        // Page is visible again
        console.log('Page visible - resume normal polling');
    }
});

// Handle beforeunload to warn user about ongoing processes
window.addEventListener('beforeunload', (e) => {
    const subtitleGen = window.subtitleGenerator;
    if (subtitleGen && subtitleGen.currentTaskId && subtitleGen.statusCheckInterval) {
        e.preventDefault();
        e.returnValue = 'Proses generate subtitle sedang berjalan. Yakin ingin meninggalkan halaman?';
        return e.returnValue;
    }
});
