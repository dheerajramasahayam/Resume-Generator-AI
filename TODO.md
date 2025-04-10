# Resume Generator AI - TODO List

This file outlines potential improvements and future enhancements for the application, categorized by priority based on the latest review.

## Immediate / High Priority

*   **Cleanup:**
    *   [ ] Delete the unused `backend/main_routes.py` file.
*   **Deployment:**
    *   [ ] Switch `systemd` service from `flask run` to a production WSGI server (Gunicorn or Waitress). *(Crucial for stability/performance)*.
    *   [ ] Properly configure Nginx reverse proxy (correct paths, SSL/HTTPS setup). *(Crucial for security/accessibility)*.
*   **Core Functionality / Bug Fixes:**
    *   [ ] Thoroughly test all existing features after recent refactoring and fixes.
    *   [X] Review and improve error handling (Backend: Standardized JSON/flash messages in API/Admin routes).
    *   [ ] Review and improve error handling (Frontend: Clearer messages for API errors).
*   **Security:**
    *   [ ] Implement CSRF protection (e.g., using `Flask-WTF`). *(Medium-High importance)*.

## Medium Priority

*   **Testing:**
    *   [X] Set up `pytest` framework (`pytest.ini`, `tests/conftest.py`, basic `tests/test_app.py`).
    *   [X] Write basic unit/integration tests for auth routes (`tests/test_auth.py`).
    *   [X] Write basic tests for profile API endpoints (`tests/test_profile_api.py`).
    *   [X] Write basic tests for generation/keyword API endpoints (`tests/test_generation_api.py`).
    *   [X] Write basic tests for export API endpoint (`tests/test_export_api.py`).
    *   [X] Write basic tests for admin routes (`tests/test_admin_routes.py`).
    *   [X] Write tests for CLI commands (`tests/test_cli.py`).
*   **Admin Dashboard:**
    *   [X] Basic structure, user list, user detail view (read-only profile), toggle admin, delete user, user/generation counts implemented.
    *   [ ] Add user registration date to model and display.
    *   [ ] Add more useful info/stats (e.g., link to view user profile page as admin?).
*   **UI/UX Polish:**
    *   [X] Basic styling improvements applied.
    *   [X] Basic loading indicators added.
    *   [ ] Make login/registration smoother (use JavaScript `fetch` instead of form POST).
    *   [ ] Add global flash message display area (e.g., in a base template or via JS).
    *   [ ] Consider using a lightweight CSS framework (e.g., Pico.css, Bulma) for better consistency if desired.
*   **Security:**
    *   [ ] Add password complexity rules during registration.
    *   [ ] Review input validation across all forms/API endpoints.

## Low Priority / Future Enhancements

*   **Export Templates (Major Enhancement):**
    *   [ ] Investigate robust parsing of AI output (structured data request, Markdown parsing libraries like `mistune`).
    *   [ ] Implement advanced layouts (columns, etc.) in DOCX/PDF based on improved parsing.
    *   [ ] Add more distinct visual styling (colors, fonts, borders) to templates.
*   **AI Input Enhancement:**
    *   [ ] Add UI elements ("Improve" button).
    *   [ ] Create backend endpoint for text enhancement via Gemini.
    *   [ ] Implement frontend logic to display suggestions.
*   **Resume/Cover Letter History:**
    *   [ ] Design database models for storing generated versions.
    *   [ ] Add API endpoints for saving/retrieving history.
    *   [ ] Create UI for viewing/managing saved versions.
*   **Refinements:**
    *   [ ] Make number of keywords configurable instead of hardcoded.
    *   [ ] Handle NLTK downloads more gracefully (e.g., during setup script).
*   **Deployment & DevOps:**
    *   [ ] Containerize with Docker (`Dockerfile`).
    *   [ ] Set up basic CI/CD pipeline (e.g., GitHub Actions for linting/testing).
