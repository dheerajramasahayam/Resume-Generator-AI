# Resume Generator AI

This web application helps users generate professional resumes and cover letters tailored to specific job descriptions using the Google Gemini API.

## Features

*   **User Authentication:** Secure registration and login.
*   **Profile Management:** Save and update personal information, work experience, education, skills, and projects.
*   **AI-Powered Resume Generation:** Generates resumes based on user profile and a target job description using Google Gemini.
*   **AI-Powered Cover Letter Generation:** Generates cover letters based on user profile, job description, and company details.
*   **Keyword Analysis:** Extracts keywords from job descriptions and highlights matches/misses with the user's profile skills.
*   **Export Options:** Export generated resumes as DOCX or PDF with basic template choices (Simple, Classic, Modern).
*   **Admin Dashboard (Foundation):** Basic structure for viewing users (requires manual admin setup via CLI).

## Tech Stack

*   **Backend:** Python, Flask, SQLAlchemy, Flask-Login, Flask-Migrate (Alembic)
*   **AI Model:** Google Gemini API (`gemini-2.5-pro-preview-03-25`)
*   **Frontend:** HTML, CSS, Vanilla JavaScript
*   **Database:** SQLite
*   **Keyword Extraction:** NLTK
*   **File Export:** python-docx, fpdf2

## Setup and Running

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/dheerajramasahayam/Resume-Generator-AI.git
    cd Resume-Generator-AI
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```
    *(Note: Using a virtual environment (`python -m venv venv`, `source venv/bin/activate`) is recommended)*

3.  **Database Setup:**
    *   Initialize Alembic (if the `db` directory doesn't exist):
        ```bash
        export FLASK_APP=backend.app:create_app
        alembic -c alembic.ini init db # Or flask db init if it works
        ```
        *(Adjust `db/env.py` sys.path if needed)*
    *   Apply migrations:
        ```bash
        export FLASK_APP=backend.app:create_app
        alembic -c alembic.ini upgrade head # Or flask db upgrade
        ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file in the project root.
    *   Add your Google Gemini API key and a Flask secret key:
        ```dotenv
        GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
        SECRET_KEY=your_strong_random_secret_key
        ```

5.  **Run the Application:**
    ```bash
    export FLASK_APP=backend.app:create_app
    flask run
    ```
    The application will typically be available at `http://127.0.0.1:5000`.

6.  **(Optional) Create Admin User:**
    *   Register a user through the web interface.
    *   Run the following command in your terminal:
        ```bash
        export FLASK_APP=backend.app:create_app
        flask make-admin <your_registered_username>
        ```

## TODO / Future Enhancements

*   Implement full Admin Dashboard UI (user management).
*   Develop more distinct visual templates for export.
*   Add AI Input Enhancement feature.
*   Implement Resume Versioning/History.
*   Add more robust error handling and user feedback.
*   Write automated tests (unit, integration).
*   Improve UI/UX.
*   Containerize with Docker.
*   Set up CI/CD pipeline (e.g., GitHub Actions).
