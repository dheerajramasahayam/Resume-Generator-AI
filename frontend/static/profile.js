document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profile-form');
    const experienceEntries = document.getElementById('experience-entries');
    const educationEntries = document.getElementById('education-entries');
    const projectEntries = document.getElementById('project-entries');
    const skillsList = document.getElementById('skills-list');
    const newSkillInput = document.getElementById('new-skill-input');
    const addSkillBtn = document.getElementById('add-skill-btn');

    const addExperienceBtn = document.getElementById('add-experience');
    const addEducationBtn = document.getElementById('add-education');
    const addProjectBtn = document.getElementById('add-project');

    const experienceTemplate = document.getElementById('experience-template');
    const educationTemplate = document.getElementById('education-template');
    const projectTemplate = document.getElementById('project-template');
    const skillTemplate = document.getElementById('skill-template');

    const saveStatus = document.getElementById('save-status');
    const usernameDisplay = document.getElementById('username-display'); // Get username from template for now

    // --- Load existing profile data ---
    async function loadProfileData() {
        try {
            const response = await fetch('/api/get_profile');
            if (!response.ok) {
                if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            populateForm(data);
        } catch (error) {
            console.error('Error loading profile data:', error);
            saveStatus.textContent = 'Error loading profile data.';
            saveStatus.className = 'status-message error';
        }
    }

    // --- Populate form with loaded data ---
    function populateForm(data) {
        // Display Username
        if (data.username && usernameDisplay) {
             usernameDisplay.textContent = data.username;
        }

        // Personal Info
        if (data.personal_info) {
            document.getElementById('full_name').value = data.personal_info.full_name || '';
            document.getElementById('phone_number').value = data.personal_info.phone_number || '';
            document.getElementById('email_address').value = data.personal_info.email_address || '';
            document.getElementById('linkedin_url').value = data.personal_info.linkedin_url || '';
            document.getElementById('portfolio_url').value = data.personal_info.portfolio_url || '';
            document.getElementById('location').value = data.personal_info.location || '';
            document.getElementById('target_job').value = data.personal_info.target_job || '';
        }

        // Experiences
        experienceEntries.innerHTML = ''; // Clear existing
        data.experiences?.forEach(exp => addExperienceEntry(exp));

        // Educations
        educationEntries.innerHTML = ''; // Clear existing
        data.educations?.forEach(edu => addEducationEntry(edu));

        // Skills
        skillsList.innerHTML = ''; // Clear existing
        data.skills?.forEach(skill => addSkillToList(skill.skill_name));

        // Projects
        projectEntries.innerHTML = ''; // Clear existing
        data.projects?.forEach(proj => addProjectEntry(proj));
    }

    // --- Add Entry Functions (Experience, Education, Project) ---
    function addExperienceEntry(data = {}) {
        const templateContent = experienceTemplate.content.cloneNode(true);
        const entryDiv = templateContent.querySelector('.experience-entry');
        if (data.job_title) entryDiv.querySelector('[name="exp_job_title"]').value = data.job_title;
        if (data.company_name) entryDiv.querySelector('[name="exp_company_name"]').value = data.company_name;
        if (data.location) entryDiv.querySelector('[name="exp_location"]').value = data.location;
        if (data.start_date) entryDiv.querySelector('[name="exp_start_date"]').value = data.start_date;
        if (data.end_date) entryDiv.querySelector('[name="exp_end_date"]').value = data.end_date;
        if (data.description) entryDiv.querySelector('[name="exp_description"]').value = data.description;

        entryDiv.querySelector('.remove-entry').addEventListener('click', () => entryDiv.remove());
        experienceEntries.appendChild(templateContent);
    }

    function addEducationEntry(data = {}) {
        const templateContent = educationTemplate.content.cloneNode(true);
        const entryDiv = templateContent.querySelector('.education-entry');
        if (data.degree_name) entryDiv.querySelector('[name="edu_degree_name"]').value = data.degree_name;
        if (data.major) entryDiv.querySelector('[name="edu_major"]').value = data.major;
        if (data.institution_name) entryDiv.querySelector('[name="edu_institution_name"]').value = data.institution_name;
        if (data.location) entryDiv.querySelector('[name="edu_location"]').value = data.location;
        if (data.graduation_date) entryDiv.querySelector('[name="edu_graduation_date"]').value = data.graduation_date;

        entryDiv.querySelector('.remove-entry').addEventListener('click', () => entryDiv.remove());
        educationEntries.appendChild(templateContent);
    }

     function addProjectEntry(data = {}) {
        const templateContent = projectTemplate.content.cloneNode(true);
        const entryDiv = templateContent.querySelector('.project-entry');
        if (data.project_name) entryDiv.querySelector('[name="proj_project_name"]').value = data.project_name;
        if (data.description) entryDiv.querySelector('[name="proj_description"]').value = data.description;
        if (data.link) entryDiv.querySelector('[name="proj_link"]').value = data.link;

        entryDiv.querySelector('.remove-entry').addEventListener('click', () => entryDiv.remove());
        projectEntries.appendChild(templateContent);
    }

    // --- Skill Management ---
    function addSkillToList(skillName) {
        if (!skillName || skillName.trim() === '') return;
        // Check if skill already exists (case-insensitive)
        const existingSkills = Array.from(skillsList.querySelectorAll('.skill-name')).map(span => span.textContent.toLowerCase());
        if (existingSkills.includes(skillName.trim().toLowerCase())) {
            return; // Don't add duplicates
        }

        const templateContent = skillTemplate.content.cloneNode(true);
        const skillItem = templateContent.querySelector('.skill-item');
        skillItem.querySelector('.skill-name').textContent = skillName.trim();
        skillItem.querySelector('.remove-skill').addEventListener('click', () => skillItem.remove());
        skillsList.appendChild(templateContent);
    }

    addSkillBtn.addEventListener('click', () => {
        addSkillToList(newSkillInput.value);
        newSkillInput.value = ''; // Clear input
        newSkillInput.focus();
    });

    newSkillInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission
            addSkillToList(newSkillInput.value);
            newSkillInput.value = '';
        }
    });


    // --- Event Listeners for Add Buttons ---
    addExperienceBtn.addEventListener('click', () => addExperienceEntry());
    addEducationBtn.addEventListener('click', () => addEducationEntry());
    addProjectBtn.addEventListener('click', () => addProjectEntry());

    // --- Save Profile Data ---
    const saveProfileBtn = document.getElementById('save-profile'); // Get button

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        saveStatus.textContent = 'Saving...';
        saveStatus.className = 'status-message';
        saveProfileBtn.disabled = true; // Disable button

        const formData = {
            personal_info: {
                full_name: document.getElementById('full_name').value,
                phone_number: document.getElementById('phone_number').value,
                email_address: document.getElementById('email_address').value,
                linkedin_url: document.getElementById('linkedin_url').value,
                portfolio_url: document.getElementById('portfolio_url').value,
                location: document.getElementById('location').value,
                target_job: document.getElementById('target_job').value,
            },
            experiences: [],
            educations: [],
            skills: [],
            projects: []
        };

        // Collect experiences
        experienceEntries.querySelectorAll('.experience-entry').forEach(entry => {
            formData.experiences.push({
                job_title: entry.querySelector('[name="exp_job_title"]').value,
                company_name: entry.querySelector('[name="exp_company_name"]').value,
                location: entry.querySelector('[name="exp_location"]').value,
                start_date: entry.querySelector('[name="exp_start_date"]').value,
                end_date: entry.querySelector('[name="exp_end_date"]').value,
                description: entry.querySelector('[name="exp_description"]').value,
            });
        });

        // Collect educations
        educationEntries.querySelectorAll('.education-entry').forEach(entry => {
            formData.educations.push({
                degree_name: entry.querySelector('[name="edu_degree_name"]').value,
                major: entry.querySelector('[name="edu_major"]').value,
                institution_name: entry.querySelector('[name="edu_institution_name"]').value,
                location: entry.querySelector('[name="edu_location"]').value,
                graduation_date: entry.querySelector('[name="edu_graduation_date"]').value,
            });
        });

        // Collect skills
        skillsList.querySelectorAll('.skill-item .skill-name').forEach(skillSpan => {
             formData.skills.push({ skill_name: skillSpan.textContent });
        });

        // Collect projects
        projectEntries.querySelectorAll('.project-entry').forEach(entry => {
            formData.projects.push({
                project_name: entry.querySelector('[name="proj_project_name"]').value,
                description: entry.querySelector('[name="proj_description"]').value,
                link: entry.querySelector('[name="proj_link"]').value,
            });
        });

        try {
            const response = await fetch('/api/save_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (response.ok) {
                saveStatus.textContent = result.message || 'Profile saved successfully!';
                saveStatus.className = 'status-message';
            } else {
                 if (response.status === 401) { // Unauthorized
                    window.location.href = '/auth/login'; // Redirect to login
                    return;
                }
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error saving profile:', error);
            saveStatus.textContent = `Error saving profile: ${error.message}`;
            saveStatus.className = 'status-message error';
        } finally {
            saveProfileBtn.disabled = false; // Re-enable button
            // Optionally clear the status message after a few seconds
            setTimeout(() => { saveStatus.textContent = ''; }, 5000);
        }
    });

    // --- Initial Load ---
    loadProfileData();
    // Add default empty entries if needed for new users
    // if (experienceEntries.children.length === 0) addExperienceEntry();
    // if (educationEntries.children.length === 0) addEducationEntry();
    // if (projectEntries.children.length === 0) addProjectEntry();
});
