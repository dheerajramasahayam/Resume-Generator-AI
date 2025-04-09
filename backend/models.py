from .app import db # Import db instance from app.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False) # Admin flag

    # Relationships
    personal_info = db.relationship('PersonalInfo', backref='user', uselist=False, cascade="all, delete-orphan")
    experiences = db.relationship('Experience', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    educations = db.relationship('Education', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    skills = db.relationship('Skill', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class PersonalInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    email_address = db.Column(db.String(120))
    linkedin_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    location = db.Column(db.String(100))
    target_job = db.Column(db.String(150)) # Added target job here as it's profile-level
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    def __repr__(self):
        return f'<PersonalInfo {self.full_name}>'

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150))
    location = db.Column(db.String(100))
    start_date = db.Column(db.String(20)) # Using String for flexibility (e.g., "Jan 2020")
    end_date = db.Column(db.String(20)) # Using String (e.g., "Present" or "Dec 2022")
    description = db.Column(db.Text) # Key Responsibilities/Achievements
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Experience {self.job_title} at {self.company_name}>'

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree_name = db.Column(db.String(150), nullable=False)
    major = db.Column(db.String(150))
    institution_name = db.Column(db.String(150))
    location = db.Column(db.String(100))
    graduation_date = db.Column(db.String(20)) # Using String for flexibility
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Education {self.degree_name} from {self.institution_name}>'

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    # category = db.Column(db.String(50)) # Optional: e.g., 'Technical', 'Soft'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Skill {self.skill_name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    link = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.project_name}>'
