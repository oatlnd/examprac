from flask import request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from PIL import Image
from app import app, db
from models import Subject, Question, Answer, Quiz, QuizQuestion
import random

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

def resize_image(image_path, max_size=(800, 600)):
    """Resize image to max_size while maintaining aspect ratio"""
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)

@app.route('/admin/add_subject', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    name = request.form['name']
    year_level = int(request.form['year_level'])
    description = request.form.get('description', '')
    
    subject = Subject(name=name, year_level=year_level, description=description)
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/add_question', methods=['POST'])
@login_required
def add_question():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        subject_id = int(request.form['subject_id'])
        question_text = request.form['question_text']
        complexity = request.form['complexity']
        question_type = request.form['question_type']
        explanation = request.form.get('explanation', '')
        
        # Handle question image upload
        question_image = None
        if 'question_image' in request.files:
            file = request.files['question_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"q_{hash(question_text + str(subject_id))}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'questions', filename)
                file.save(filepath)
                resize_image(filepath)
                question_image = f"uploads/questions/{filename}"
        
        question = Question(
            subject_id=subject_id,
            question_text=question_text,
            question_image=question_image,
            complexity=complexity,
            question_type=question_type,
            explanation=explanation
        )
        
        db.session.add(question)
        db.session.flush()  # To get the question ID
        
        # Add answers
        if question_type == 'multiple_choice':
            for i in range(1, 5):  # Up to 4 answers
                answer_text = request.form.get(f'answer_{i}')
                if answer_text:
                    is_correct = request.form.get(f'correct_{i}') == 'on'
                    
                    # Handle answer image
                    answer_image = None
                    if f'answer_image_{i}' in request.files:
                        file = request.files[f'answer_image_{i}']
                        if file and file.filename and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            filename = f"a_{question.id}_{i}_{filename}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'answers', filename)
                            file.save(filepath)
                            resize_image(filepath)
                            answer_image = f"uploads/answers/{filename}"
                    
                    answer = Answer(
                        question_id=question.id,
                        answer_text=answer_text,
                        answer_image=answer_image,
                        is_correct=is_correct
                    )
                    db.session.add(answer)
        
        elif question_type == 'short_answer':
            correct_answers = request.form.get('correct_answers', '').split('|')
            for ans in correct_answers:
                if ans.strip():
                    answer = Answer(
                        question_id=question.id,
                        answer_text=ans.strip(),
                        is_correct=True
                    )
                    db.session.add(answer)
        
        db.session.commit()
        flash('Question added successfully')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding question: {str(e)}')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/generate_quiz', methods=['POST'])
@login_required
def generate_quiz():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        title = request.form['title']
        subject_id = int(request.form['subject_id'])
        complexity = request.form['complexity']
        num_questions = int(request.form.get('num_questions', 10))
        time_limit = request.form.get('time_limit')
        time_limit = int(time_limit) if time_limit else None
        
        # Create quiz
        quiz = Quiz(
            title=title,
            subject_id=subject_id,
            complexity_filter=complexity,
            time_limit=time_limit,
            total_questions=num_questions
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Get questions based on criteria
        query = Question.query.filter_by(subject_id=subject_id)
        
        if complexity != 'mixed':
            query = query.filter_by(complexity=complexity)
        
        available_questions = query.all()
        
        if len(available_questions) < num_questions:
            flash(f'Not enough questions available. Found {len(available_questions)}, need {num_questions}')
            db.session.rollback()
            return redirect(url_for('admin_questions'))
        
        # Randomly select questions
        selected_questions = random.sample(available_questions, num_questions)
        
        # Add questions to quiz
        for i, question in enumerate(selected_questions):
            quiz_question = QuizQuestion(
                quiz_id=quiz.id,
                question_id=question.id,
                order_index=i + 1
            )
            db.session.add(quiz_question)
        
        db.session.commit()
        flash(f'Quiz "{title}" generated successfully with {num_questions} questions')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error generating quiz: {str(e)}')
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/delete_question/<int:question_id>')
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    question = Question.query.get_or_404(question_id)
    
    # Delete associated image files
    if question.question_image:
        image_path = os.path.join('static', question.question_image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    for answer in question.answers:
        if answer.answer_image:
            image_path = os.path.join('static', answer.answer_image)
            if os.path.exists(image_path):
                os.remove(image_path)
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully')
    return redirect(url_for('admin_questions'))

@app.route('/admin/edit_question/<int:question_id>')
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    question = Question.query.get_or_404(question_id)
    subjects = Subject.query.all()
    
    return render_template('admin/edit_question.html', question=question, subjects=subjects)