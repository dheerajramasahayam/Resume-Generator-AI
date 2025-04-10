document.addEventListener('DOMContentLoaded', () => {
    const generateForm = document.getElementById('generate-form');
    const jobDescriptionInput = document.getElementById('job_description');
    const generateBtn = document.getElementById('generate-btn');
    const generateStatus = document.getElementById('generate-status');
    const profileCheckMessage = document.getElementById('profile-check-message');
    // const loadingIndicator = document.getElementById('loading-indicator'); // Remove this line
    // Keyword elements
    const analyzeKeywordsBtn = document.getElementById('analyze-keywords-btn');
    const keywordLoading = document.getElementById('keyword-loading');
    const keywordsOutput = document.getElementById('keywords-output');
    const keywordMatchInfo = document.getElementById('keyword-match-info');

    let userSkills = []; // To store user's skills for comparison

    // --- Check if profile exists and fetch skills ---
    async function checkProfileAndFetchSkills() { // Renamed function
        try {
            const response = await fetch('/api/get_profile');
            if (!response.ok) {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return false;
                }
                // Assume other errors mean profile might exist but couldn't be fetched fully
                console.warn('Could not fully verify profile existence, proceeding cautiously.');
                return true; // Allow generation attempt
            }
            const data = await response.json();

            // Store user skills (lowercase for easier comparison)
            userSkills = data.skills?.map(skill => skill.skill_name.toLowerCase()) || [];

            // Basic check: Does personal info or experience exist?
            const profileExists = (data.personal_info && data.personal_info.full_name) || (data.experiences && data.experiences.length > 0);

            if (!profileExists) {
                profileCheckMessage.style.display = 'block';
                generateBtn.disabled = true;
                return false;
            } else {
                profileCheckMessage.style.display = 'none';
                generateBtn.disabled = false;
                return true;
            }
        } catch (error) {
            console.error('Error checking profile:', error);
            // Allow generation attempt if check fails, backend will handle it
            generateStatus.textContent = 'Could not verify profile status. Proceed with caution.';
            generateStatus.className = 'status-message warning'; // Use a warning style
            generateBtn.disabled = false; // Enable button but show warning
            return true;
        }
    }

    // --- Handle Keyword Analysis ---
    analyzeKeywordsBtn.addEventListener('click', async () => {
        const jobDescription = jobDescriptionInput.value;
        if (!jobDescription.trim()) {
            keywordsOutput.innerHTML = '<p class="error">Please paste a job description first.</p>';
            return;
        }

        keywordsOutput.innerHTML = ''; // Clear previous results
        keywordMatchInfo.innerHTML = '';
        keywordLoading.style.display = 'block';
        analyzeKeywordsBtn.disabled = true;

        try {
            const response = await fetch('/api/extract_keywords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ job_description: jobDescription }),
            });

            const result = await response.json();

            if (response.ok) {
                displayKeywords(result.keywords);
                compareKeywords(result.keywords);
                if (result.warning) {
                     keywordsOutput.innerHTML += `<p class="warning">${result.warning}</p>`;
                }
            } else {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error('Error analyzing keywords:', error);
            keywordsOutput.innerHTML = `<p class="error">Error analyzing keywords: ${error.message}</p>`;
        } finally {
            keywordLoading.style.display = 'none';
            analyzeKeywordsBtn.disabled = false;
        }
    });

    function displayKeywords(keywords) {
        if (!keywords || keywords.length === 0) {
            keywordsOutput.innerHTML = '<p>No significant keywords found.</p>';
            return;
        }
        let html = '<strong>Extracted Keywords:</strong><ul class="keyword-list">';
        keywords.forEach(kw => {
            // Check if user has this skill (case-insensitive)
            const hasSkill = userSkills.includes(kw.toLowerCase());
            html += `<li class="${hasSkill ? 'match' : 'miss'}">${kw} ${hasSkill ? '✓' : '✗'}</li>`;
        });
        html += '</ul>';
        keywordsOutput.innerHTML = html;

        // Add some basic styling for keywords if needed in style.css later
        // e.g., .keyword-list { list-style: none; padding: 0; }
        // .keyword-list li { display: inline-block; margin: 3px; padding: 3px 6px; border-radius: 3px; }
        // .keyword-list li.match { background-color: #d4edda; border: 1px solid #c3e6cb; }
        // .keyword-list li.miss { background-color: #f8d7da; border: 1px solid #f5c6cb; }
    }

     function compareKeywords(extractedKeywords) {
        if (!userSkills || userSkills.length === 0) {
            keywordMatchInfo.textContent = 'Add skills to your profile to see matches.';
            return;
        }
        const extractedLower = extractedKeywords.map(kw => kw.toLowerCase());
        const matchedSkills = userSkills.filter(skill => extractedLower.includes(skill));
        const missingKeywords = extractedKeywords.filter(kw => !userSkills.includes(kw.toLowerCase()));

        let matchHtml = '';
        if (matchedSkills.length > 0) {
            matchHtml += `You have ${matchedSkills.length} matching skill(s) in your profile. `;
        }
        if (missingKeywords.length > 0) {
             matchHtml += `${missingKeywords.length} keyword(s) found in the job description might be missing from your profile skills. Consider adding relevant ones.`;
        } else if (matchedSkills.length > 0) {
            matchHtml += `Good job matching the key terms!`;
        } else {
             matchHtml += `No direct matches found between extracted keywords and your profile skills.`;
        }
        keywordMatchInfo.innerHTML = matchHtml;
    }


    // --- Handle Generation Request ---
    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        generateStatus.textContent = ''; // Clear previous status
        generateStatus.className = 'status-message';
        const originalButtonText = generateBtn.textContent; // Store original text
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...'; // Change button text

        const jobDescription = jobDescriptionInput.value;

        if (!jobDescription.trim()) {
            generateStatus.textContent = 'Job description cannot be empty.';
            generateStatus.className = 'status-message error';
            generateBtn.disabled = false;
            generateBtn.textContent = originalButtonText; // Restore button text
            return;
        }

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ job_description: jobDescription }),
            });

            const result = await response.json();

            if (response.ok) {
                // Store the result in sessionStorage to pass to the next page
                sessionStorage.setItem('generatedResume', result.resume_text);
                // Redirect to the resume display page
                window.location.href = '/resume_display';
            } else {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error('Error generating resume:', error);
            generateStatus.textContent = `Error generating resume: ${error.message}`;
            generateStatus.className = 'status-message error';
        } finally {
            generateBtn.disabled = false; // Re-enable button
            generateBtn.textContent = originalButtonText; // Restore button text
        }
    });

    // --- Initial Check ---
    checkProfileAndFetchSkills(); // Call the renamed function
});
