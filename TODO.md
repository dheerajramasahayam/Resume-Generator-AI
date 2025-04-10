# Resume Generator AI - TODO List

This file outlines potential improvements and future enhancements for the application, categorized by priority.

## Immediate / High Priority

*   **Cleanup:**
    *   [ ] Delete the unused `backend/main_routes.py` file.
*   **Deployment:**
    *   [ ] Switch `systemd` service from `flask run` to a production WSGI server (Gunicorn or Waitress). *(Crucial for stability/performance if deployed)*.
    *   [ ] Properly configure Nginx reverse proxy (including correct paths, potentially SSL/HTTPS setup). *(Crucial for security/accessibility if deployed)*.
*   **Bug Fixes / Core Functionality:**
    *   [ ] Thoroughly test all existing features after recent refactoring and fixes.
    *   [ ] Review and improve error handling (both frontend and backend) for API calls and unexpected situations.

## Medium Priority

*   **Admin Dashboard:**
    *   [X] Create `frontend/admin/admin_user_detail.html` template.
    *   [X] Update `view_user` route in `admin_routes.py` to render the detail template.
    *   [X] Add Toggle Admin / Delete User functionality.
    *   [X] Add user count to dashboard.
    *   [X] Add generation counts to User model, increment in API, display in admin views.
    *   [ ] Add more useful info/stats to the admin dashboard (e.g., date registered).
*   **Testing:**
    *   [ ] Set up `pytest`.
    *   [ ] Write basic unit/integration tests for core API endpoints (auth, profile save/load, generation).
*   **Security:**
    *   [ ] Implement CSRF protection (e.g., using `Flask-WTF` or similar).
    *   [ ] Review all points of user input for potential security vulnerabilities (though SQLAlchemy helps prevent basic SQL injection).
*   **UI/UX Polish:**
    *   [X] Add better loading indicators/feedback during API calls (e.g., disable buttons, change text).
    *   [X] Improve visual consistency and styling (Refined existing CSS: fonts, spacing, borders, colors, buttons).
    *   [ ] Make login/registration smoother (e.g., using JavaScript `fetch` to avoid full page reloads and show messages dynamically).

## Low Priority / Future Enhancements

*   **Export Templates (Major Enhancement):**
    *   [ ] Investigate robust parsing of AI output (structured data request, Markdown parsing libraries).
    *   [ ] Implement advanced layouts (columns, etc.) in DOCX/PDF based on improved parsing.
    *   [ ] Add more distinct visual styling (colors, fonts, borders) to templates.
*   **AI Input Enhancement:**
    *   [ ] Add UI elements (e.g., "Improve" button next to text areas).
    *   [ ] Create backend endpoint to send specific text + enhancement prompt to Gemini.
    *   [ ] Implement frontend logic to display suggestions.
*   **Resume/Cover Letter History:**
    *   [ ] Design database models for storing generated versions.
    *   [ ] Add API endpoints for saving and retrieving history.
    *   [ ] Create UI for viewing/managing saved versions.
*   **Containerization:**
    *   [ ] Create a `Dockerfile` to containerize the application for easier deployment.
*   **CI/CD:**
    *   [ ] Set up GitHub Actions (or other platform) workflow to run linter (`ruff`) and tests (`pytest`) automatically.
    *   [ ] Potentially add automated deployment steps.
