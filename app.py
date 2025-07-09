from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import secrets
from PIL import Image
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_practice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'questions'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'answers'), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Stripe configuration (you'll need to add your keys)
stripe.api_key = "sk_test_your_stripe_secret_key"  # Replace with your actual key

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from models import User
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        year_level = request.form['year_level']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            year_level=int(year_level),
            trial_expires=datetime.utcnow() + timedelta(days=7)  # 7-day free trial
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! You have a 7-day free trial.')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import User
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Subject
    # Check subscription status
    has_access = current_user.has_active_subscription()
    subjects = Subject.query.filter_by(year_level=current_user.year_level).all()
    return render_template('dashboard.html', has_access=has_access, subjects=subjects)

@app.route('/admin')
@login_required
def admin_dashboard():
    from models import User, Question, Subject
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    total_users = User.query.count()
    total_questions = Question.query.count()
    total_subjects = Subject.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_questions=total_questions,
                         total_subjects=total_subjects)

@app.route('/admin/subjects')
@login_required
def admin_subjects():
    from models import Subject
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/questions')
@login_required
def admin_questions():
    from models import Question, Subject
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    questions = Question.query.all()
    subjects = Subject.query.all()
    return render_template('admin/questions.html', questions=questions, subjects=subjects)

@app.route('/subscription')
@login_required
def subscription():
    return render_template('subscription.html')

@app.route('/quiz/<int:subject_id>')
@login_required
def take_quiz(subject_id):
    from models import Subject, Question
    if not current_user.has_active_subscription():
        flash('Please subscribe to access quizzes')
        return redirect(url_for('subscription'))
    
    subject = Subject.query.get_or_404(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).limit(10).all()
    
    return render_template('quiz.html', subject=subject, questions=questions)

# Import admin routes to register them
import admin_routes

if __name__ == '__main__':
    with app.app_context():
        from models import User, Subject, Question, Answer
        
        db.create_all()
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                year_level=12
            )
            db.session.add(admin)
            db.session.commit()
        
        # Create sample subjects if they don't exist
        if Subject.query.count() == 0:
            subjects = [
                Subject(name='Mathematics', year_level=10, description='Algebra, Geometry, and Statistics'),
                Subject(name='Science', year_level=10, description='Physics, Chemistry, and Biology'),
                Subject(name='English', year_level=10, description='Literature, Grammar, and Writing'),
                Subject(name='Mathematics', year_level=11, description='Advanced Algebra and Calculus'),
                Subject(name='Science', year_level=11, description='Advanced Physics and Chemistry'),
            ]
            
            for subject in subjects:
                db.session.add(subject)
            
            db.session.commit()
            
            # Create sample questions
            math_subject = Subject.query.filter_by(name='Mathematics', year_level=10).first()
            if math_subject and Question.query.count() == 0:
                question1 = Question(
                    subject_id=math_subject.id,
                    question_text='What is the value of x in the equation 2x + 5 = 15?',
                    complexity='low',
                    question_type='multiple_choice',
                    explanation='Subtract 5 from both sides: 2x = 10, then divide by 2: x = 5'
                )
                db.session.add(question1)
                db.session.flush()
                
                # Add answers
                answers = [
                    Answer(question_id=question1.id, answer_text='x = 3', is_correct=False),
                    Answer(question_id=question1.id, answer_text='x = 5', is_correct=True),
                    Answer(question_id=question1.id, answer_text='x = 7', is_correct=False),
                    Answer(question_id=question1.id, answer_text='x = 10', is_correct=False),
                ]
                
                for answer in answers:
                    db.session.add(answer)
                
                question2 = Question(
                    subject_id=math_subject.id,
                    question_text='Solve for y: 3y - 7 = 2y + 8',
                    complexity='medium',
                    question_type='short_answer',
                    explanation='Subtract 2y from both sides: y - 7 = 8, then add 7: y = 15'
                )
                db.session.add(question2)
                db.session.flush()
                
                short_answers = [
                    Answer(question_id=question2.id, answer_text='15', is_correct=True),
                    Answer(question_id=question2.id, answer_text='y = 15', is_correct=True),
                ]
                
                for answer in short_answers:
                    db.session.add(answer)
                
                db.session.commit()
    
    app.run(debug=True)