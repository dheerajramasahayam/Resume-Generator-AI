document.addEventListener('DOMContentLoaded', () => {
    const resumeOutputDiv = document.getElementById('resume-output');
    const copyBtn = document.getElementById('copy-btn');
    const exportDocxBtn = document.getElementById('export-docx-btn'); // New button
    const exportPdfBtn = document.getElementById('export-pdf-btn');   // New button
    const copyStatus = document.getElementById('copy-status');
    const exportStatus = document.getElementById('export-status'); // New status element

    // --- Load resume from sessionStorage ---
    function loadResume() {
        const resumeText = sessionStorage.getItem('generatedResume');
        if (resumeText) {
            // Display the resume text
            // Replace newlines with <br> for HTML display, but keep original for copy
            // resumeOutputDiv.innerHTML = resumeText.replace(/\n/g, '<br>');
            // Clean the text for display (remove markdown markers)
            let displayText = resumeText;
            displayText = displayText.replace(/^###\s+/gm, ''); // Remove ### heading marker
            displayText = displayText.replace(/\*\*(.*?)\*\*/g, '$1'); // Remove ** bold marker
            displayText = displayText.replace(/^\*\s+/gm, '• '); // Replace * list marker with a bullet

            // Using <pre> tag might be better for formatting preservation
            const pre = document.createElement('pre');
            pre.textContent = displayText; // Display cleaned text
            resumeOutputDiv.innerHTML = ''; // Clear loading message
            resumeOutputDiv.appendChild(pre);

            // Optionally clear the sessionStorage item after loading
            // sessionStorage.removeItem('generatedResume');
        } else {
            resumeOutputDiv.textContent = 'No resume data found. Please generate a resume first.';
            copyBtn.disabled = true;
            exportDocxBtn.disabled = true; // Disable export if no resume
            exportPdfBtn.disabled = true;  // Disable export if no resume
        }
    }

    // --- Copy to Clipboard ---
    copyBtn.addEventListener('click', async () => {
        const resumeText = sessionStorage.getItem('generatedResume'); // Get original text
        if (!resumeText || !navigator.clipboard) {
            copyStatus.textContent = 'Failed to copy (Clipboard API not available or no text).';
            copyStatus.className = 'status-message error';
            return;
        }

        try {
            await navigator.clipboard.writeText(resumeText);
            copyStatus.textContent = 'Resume copied to clipboard!';
            copyStatus.className = 'status-message';
        } catch (err) {
            console.error('Failed to copy text: ', err);
            copyStatus.textContent = 'Failed to copy resume.';
            copyStatus.className = 'status-message error';
        } finally {
             // Optionally clear the status message after a few seconds
            setTimeout(() => { copyStatus.textContent = ''; }, 3000);
        }
    });

    // --- Export Functionality ---
    async function handleExport(format) {
        const resumeText = sessionStorage.getItem('generatedResume');
        // Get selected template
        const selectedTemplate = document.querySelector('input[name="export_template"]:checked').value;

        if (!resumeText) {
            exportStatus.textContent = 'No resume text found to export.';
            exportStatus.className = 'status-message error';
            return;
        }

        exportStatus.textContent = `Exporting as ${format.toUpperCase()}...`;
        exportStatus.className = 'status-message';
        exportDocxBtn.disabled = true; // Disable buttons during export
        exportPdfBtn.disabled = true;

        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resume_text: resumeText,
                    format: format,
                    template: selectedTemplate // Send template choice
                }),
            });

            if (response.ok) {
                // Trigger file download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                // Set the filename based on format
                a.download = `resume.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                exportStatus.textContent = `${format.toUpperCase()} export successful!`;
                exportStatus.className = 'status-message';
            } else {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                const errorResult = await response.json();
                throw new Error(errorResult.error || `HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error(`Error exporting as ${format}:`, error);
            exportStatus.textContent = `Error exporting as ${format}: ${error.message}`;
            exportStatus.className = 'status-message error';
        } finally {
            exportDocxBtn.disabled = false; // Re-enable buttons
            exportPdfBtn.disabled = false;
             // Optionally clear the status message after a few seconds
            setTimeout(() => { exportStatus.textContent = ''; }, 5000);
        }
    }

    exportDocxBtn.addEventListener('click', () => handleExport('docx'));
    exportPdfBtn.addEventListener('click', () => handleExport('pdf'));


    // --- Initial Load ---
    loadResume();
});
