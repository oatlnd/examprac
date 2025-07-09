from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    year_level = db.Column(db.Integer, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trial_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    
    def has_active_subscription(self):
        # Check if user has active trial
        if self.trial_expires and datetime.utcnow() < self.trial_expires:
            return True
        
        # Check if user has active paid subscription
        active_sub = Subscription.query.filter_by(
            user_id=self.id,
            is_active=True
        ).filter(Subscription.expires_at > datetime.utcnow()).first()
        
        return active_sub is not None

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year_level = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(200), nullable=True)
    complexity = db.Column(db.String(20), nullable=False)  # low, medium, high
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, short_answer
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    answer_image = db.Column(db.String(200), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    complexity_filter = db.Column(db.String(20), nullable=True)  # low, medium, high, mixed
    time_limit = db.Column(db.Integer, nullable=True)  # in minutes
    total_questions = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=True)
    
    # Relationships
    responses = db.relationship('QuizResponse', backref='attempt', lazy=True)

class QuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=True)  # For multiple choice
    answer_text = db.Column(db.Text, nullable=True)  # For short answer
    is_correct = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    plan_type = db.Column(db.String(50), nullable=False)  # monthly, yearly
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)