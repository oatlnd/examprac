from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_practice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    year_group = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Subscription relationship
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False)  # 'free_trial', 'monthly', 'yearly'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    year_group = db.Column(db.Integer, nullable=False)
    complexity = db.Column(db.String(10), nullable=False)  # 'low', 'medium', 'high'
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(200))
    question_type = db.Column(db.String(20), nullable=False)  # 'multiple_choice', 'short_answer'
    
    # For multiple choice questions
    option_a = db.Column(db.Text)
    option_b = db.Column(db.Text)
    option_c = db.Column(db.Text)
    option_d = db.Column(db.Text)
    correct_option = db.Column(db.String(1))  # 'A', 'B', 'C', 'D'
    
    # For short answer questions
    correct_answer = db.Column(db.Text)
    answer_image = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    year_group = db.Column(db.Integer, nullable=False)
    complexity = db.Column(db.String(10))  # Can be mixed
    questions = db.Column(db.Text)  # JSON string of question IDs
    time_limit = db.Column(db.Integer, default=30)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.Column(db.Text)  # JSON string of answers
    score = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        year_group = request.form['year_group']
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            year_group=int(year_group)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create free trial subscription
        trial_end = datetime.utcnow() + timedelta(days=7)
        subscription = Subscription(
            user_id=user.id,
            subscription_type='free_trial',
            end_date=trial_end
        )
        db.session.add(subscription)
        db.session.commit()
        
        flash('Registration successful! You have a 7-day free trial.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    subjects = Subject.query.all()
    
    # Check subscription status
    subscription = user.subscription
    subscription_valid = subscription and subscription.end_date > datetime.utcnow()
    
    return render_template('student_dashboard.html', 
                         user=user, 
                         subjects=subjects, 
                         subscription=subscription,
                         subscription_valid=subscription_valid)

@app.route('/student/quiz/<int:subject_id>')
def select_quiz(subject_id):
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    subject = Subject.query.get_or_404(subject_id)
    
    # Check subscription
    subscription = user.subscription
    if not subscription or subscription.end_date <= datetime.utcnow():
        flash('Your subscription has expired. Please upgrade to continue.')
        return redirect(url_for('student_dashboard'))
    
    return render_template('select_quiz.html', subject=subject, user=user)

@app.route('/student/take_quiz', methods=['POST'])
def take_quiz():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    subject_id = request.form['subject_id']
    complexity = request.form['complexity']
    num_questions = int(request.form.get('num_questions', 10))
    
    user = User.query.get(session['user_id'])
    
    # Get questions based on criteria
    questions = Question.query.filter_by(
        subject_id=subject_id,
        year_group=user.year_group,
        complexity=complexity
    ).all()
    
    if len(questions) < num_questions:
        flash(f'Not enough questions available. Only {len(questions)} questions found.')
        return redirect(url_for('select_quiz', subject_id=subject_id))
    
    # Randomly select questions
    selected_questions = random.sample(questions, num_questions)
    
    return render_template('take_quiz.html', questions=selected_questions, subject_id=subject_id)

@app.route('/student/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect(url_for('login'))
    
    # Process quiz submission and calculate score
    answers = {}
    score = 0
    total_questions = 0
    
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            answers[question_id] = value
            
            question = Question.query.get(question_id)
            total_questions += 1
            
            if question.question_type == 'multiple_choice':
                if value == question.correct_option:
                    score += 1
            else:  # short_answer
                # Simple string comparison (could be enhanced with fuzzy matching)
                if value.lower().strip() == question.correct_answer.lower().strip():
                    score += 1
    
    percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Save quiz attempt
    attempt = QuizAttempt(
        user_id=session['user_id'],
        quiz_id=1,  # For custom quizzes, we can use a default ID or create dynamic quizzes
        answers=str(answers),
        score=percentage_score
    )
    db.session.add(attempt)
    db.session.commit()
    
    return render_template('quiz_results.html', 
                         score=score, 
                         total=total_questions, 
                         percentage=percentage_score)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    total_users = User.query.count()
    total_questions = Question.query.count()
    total_subjects = Subject.query.count()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_questions=total_questions,
                         total_subjects=total_subjects)

@app.route('/admin/subjects')
def manage_subjects():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    subjects = Subject.query.all()
    return render_template('manage_subjects.html', subjects=subjects)

@app.route('/admin/subjects/add', methods=['POST'])
def add_subject():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    name = request.form['name']
    description = request.form.get('description', '')
    
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully!')
    return redirect(url_for('manage_subjects'))

@app.route('/admin/questions')
def manage_questions():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    questions = Question.query.paginate(page=page, per_page=20, error_out=False)
    subjects = Subject.query.all()
    
    return render_template('manage_questions.html', questions=questions, subjects=subjects)

@app.route('/admin/questions/add', methods=['GET', 'POST'])
def add_question():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle file upload
        question_image = None
        answer_image = None
        
        if 'question_image' in request.files:
            file = request.files['question_image']
            if file and file.filename:
                filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                question_image = filename
        
        if 'answer_image' in request.files:
            file = request.files['answer_image']
            if file and file.filename:
                filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                answer_image = filename
        
        question = Question(
            subject_id=request.form['subject_id'],
            year_group=request.form['year_group'],
            complexity=request.form['complexity'],
            question_text=request.form['question_text'],
            question_image=question_image,
            question_type=request.form['question_type']
        )
        
        if request.form['question_type'] == 'multiple_choice':
            question.option_a = request.form['option_a']
            question.option_b = request.form['option_b']
            question.option_c = request.form['option_c']
            question.option_d = request.form['option_d']
            question.correct_option = request.form['correct_option']
        else:
            question.correct_answer = request.form['correct_answer']
            question.answer_image = answer_image
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question added successfully!')
        return redirect(url_for('manage_questions'))
    
    subjects = Subject.query.all()
    return render_template('add_question.html', subjects=subjects)

@app.route('/admin/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        subject_id = request.form['subject_id']
        year_group = request.form['year_group']
        complexity = request.form['complexity']
        num_questions = int(request.form['num_questions'])
        
        # Get questions based on criteria
        query = Question.query.filter_by(subject_id=subject_id, year_group=year_group)
        if complexity != 'mixed':
            query = query.filter_by(complexity=complexity)
        
        questions = query.all()
        
        if len(questions) < num_questions:
            flash(f'Not enough questions available. Only {len(questions)} questions found.')
            return redirect(url_for('create_quiz'))
        
        selected_questions = random.sample(questions, num_questions)
        question_ids = [q.id for q in selected_questions]
        
        quiz = Quiz(
            title=title,
            subject_id=subject_id,
            year_group=year_group,
            complexity=complexity,
            questions=str(question_ids)
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!')
        return redirect(url_for('admin_dashboard'))
    
    subjects = Subject.query.all()
    return render_template('create_quiz.html', subjects=subjects)

@app.route('/subscription')
def subscription():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('subscription.html', user=user)

@app.route('/upgrade_subscription', methods=['POST'])
def upgrade_subscription():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    subscription_type = request.form['subscription_type']
    user = User.query.get(session['user_id'])
    
    # Calculate end date based on subscription type
    if subscription_type == 'monthly':
        end_date = datetime.utcnow() + timedelta(days=30)
    elif subscription_type == 'yearly':
        end_date = datetime.utcnow() + timedelta(days=365)
    
    # Update or create subscription
    if user.subscription:
        user.subscription.subscription_type = subscription_type
        user.subscription.end_date = end_date
        user.subscription.is_active = True
    else:
        subscription = Subscription(
            user_id=user.id,
            subscription_type=subscription_type,
            end_date=end_date
        )
        db.session.add(subscription)
    
    db.session.commit()
    flash(f'Successfully upgraded to {subscription_type} subscription!')
    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                year_group=12
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)