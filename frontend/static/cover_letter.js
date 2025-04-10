document.addEventListener('DOMContentLoaded', () => {
    const coverLetterForm = document.getElementById('cover-letter-form');
    const companyNameInput = document.getElementById('company_name');
    const hiringManagerInput = document.getElementById('hiring_manager');
    const jobDescriptionInput = document.getElementById('job_description_cl');
    const additionalNotesInput = document.getElementById('additional_notes');
    const generateBtn = document.getElementById('generate-cl-btn');
    const generateStatus = document.getElementById('generate-cl-status');
    // const loadingIndicator = document.getElementById('loading-cl-indicator'); // Remove this line
    const outputDiv = document.getElementById('cover-letter-output');
    const copyBtn = document.getElementById('copy-cl-btn');
    const copyStatus = document.getElementById('copy-cl-status');

    let generatedCoverLetter = ''; // Store the generated text

    coverLetterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        generateStatus.textContent = '';
        generateStatus.className = 'status-message';
        outputDiv.innerHTML = 'Generating...'; // Clear previous output
        copyBtn.disabled = true;
        const originalButtonText = generateBtn.textContent; // Store original text
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...'; // Change button text
        generatedCoverLetter = ''; // Reset stored text

        const payload = {
            company_name: companyNameInput.value,
            hiring_manager: hiringManagerInput.value,
            job_description: jobDescriptionInput.value,
            additional_notes: additionalNotesInput.value,
        };

        try {
            const response = await fetch('/api/generate_cover_letter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                generatedCoverLetter = result.cover_letter_text;
                const pre = document.createElement('pre');
                pre.textContent = generatedCoverLetter;
                outputDiv.innerHTML = ''; // Clear loading message
                outputDiv.appendChild(pre);
                generateStatus.textContent = 'Cover letter generated successfully!';
                generateStatus.className = 'status-message';
                copyBtn.disabled = false; // Enable copy button
            } else {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error('Error generating cover letter:', error);
            outputDiv.innerHTML = `<p class="error">Error generating cover letter: ${error.message}</p>`;
            generateStatus.textContent = `Error: ${error.message}`;
            generateStatus.className = 'status-message error';
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = originalButtonText; // Restore button text
             // Optionally clear the status message after a few seconds
            setTimeout(() => { generateStatus.textContent = ''; }, 5000);
        }
    });

    // --- Copy to Clipboard ---
    copyBtn.addEventListener('click', async () => {
        if (!generatedCoverLetter || !navigator.clipboard) {
            copyStatus.textContent = 'Failed to copy (Clipboard API not available or no text).';
            copyStatus.className = 'status-message error';
            return;
        }

        try {
            await navigator.clipboard.writeText(generatedCoverLetter);
            copyStatus.textContent = 'Cover letter copied to clipboard!';
            copyStatus.className = 'status-message';
        } catch (err) {
            console.error('Failed to copy text: ', err);
            copyStatus.textContent = 'Failed to copy cover letter.';
            copyStatus.className = 'status-message error';
        } finally {
             setTimeout(() => { copyStatus.textContent = ''; }, 3000);
        }
    });
});
