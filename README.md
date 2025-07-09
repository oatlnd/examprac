# ExamPractice - School Exam Preparation Platform

A comprehensive web-based exam practice platform designed for school children to improve their academic performance through structured practice and assessment.

## Features

### 🎓 Student Features
- **Multi-Subject Support**: Practice questions across various subjects organized by year/grade level
- **Free Trial**: 7-day free trial for new users with full access to all features
- **Question Types**: Support for multiple choice and short answer questions
- **Rich Content**: Questions and answers can include both text and images
- **Progress Tracking**: Monitor your improvement with detailed analytics
- **Adaptive Learning**: Questions categorized by complexity (Low, Medium, High)
- **Subscription Management**: Flexible monthly and yearly subscription plans
- **Mobile Responsive**: Study anywhere on any device

### 👨‍💼 Admin Features
- **Question Bank Management**: Create, edit, and delete questions with text and image support
- **Subject Organization**: Manage subjects across different year levels
- **Quiz Generation**: Automatically generate quizzes based on criteria (subject, year, complexity)
- **User Management**: Monitor registered users and subscription status
- **Content Analytics**: Track question usage and difficulty distribution

### 🔒 Security & Authentication
- Secure user registration and login system
- Admin-only access to management features
- Session management with Flask-Login
- Password hashing for security

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser and navigate to `http://localhost:5000`

## Default Accounts

### Admin Account
- **Email**: admin@example.com
- **Password**: admin123
- **Access**: Full admin panel access for managing questions and subjects

### Student Registration
- Create a new student account through the registration form
- All new accounts receive a 7-day free trial automatically

## Usage Guide

### For Students

1. **Register an Account**
   - Click "Get Started" on the homepage
   - Fill in your details including year/grade level
   - Enjoy your 7-day free trial!

2. **Take Practice Quizzes**
   - Browse subjects available for your year level
   - Click "Start Quiz" on any subject
   - Answer questions with the built-in timer
   - Track your progress and scores

3. **Manage Subscription**
   - View subscription status on your dashboard
   - Choose between monthly ($9) or yearly ($65) plans
   - Access the subscription page for plan details

### For Administrators

1. **Access Admin Panel**
   - Login with admin credentials
   - Navigate to Admin → Dashboard from the top menu

2. **Manage Subjects**
   - Go to Admin → Subjects
   - Add new subjects with year level and descriptions
   - View existing subjects organized by year

3. **Create Questions**
   - Go to Admin → Questions
   - Click "Add New Question"
   - Choose question type (Multiple Choice or Short Answer)
   - Add question text and optional images
   - Set complexity level (Low, Medium, High)
   - Add answer options with correct answers marked

4. **Generate Quizzes**
   - Use the "Generate Quiz" feature in the admin dashboard
   - Select subject, complexity, and number of questions
   - Set optional time limits

## File Structure

```
exam-practice/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── admin_routes.py        # Admin functionality routes
├── requirements.txt       # Python dependencies
├── static/
│   └── uploads/          # Uploaded images (questions/answers)
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Student dashboard
│   ├── subscription.html # Subscription management
│   ├── quiz.html         # Quiz taking interface
│   └── admin/            # Admin templates
│       ├── dashboard.html
│       ├── subjects.html
│       └── questions.html
└── exam_practice.db      # SQLite database (created automatically)
```

## Database Schema

### Key Models
- **User**: Student accounts with subscription tracking
- **Subject**: Subjects organized by year level
- **Question**: Questions with text/image content and complexity
- **Answer**: Answer options for questions
- **Quiz**: Generated quiz containers
- **QuizAttempt**: Student quiz attempts and scores
- **Subscription**: Subscription management and billing

## Technical Features

### Frontend
- **Bootstrap 5**: Modern, responsive UI framework
- **Font Awesome**: Professional icons throughout the application
- **Custom CSS**: Professional styling with consistent design system
- **JavaScript**: Interactive quiz interface with timer and navigation

### Backend
- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: Database ORM for easy data management
- **Flask-Login**: User session management
- **Werkzeug**: Password hashing and file uploads
- **Pillow**: Image processing and optimization

### Database
- **SQLite**: Lightweight database perfect for development and small deployments
- **Automatic migrations**: Database tables created automatically on first run

## Customization

### Adding New Question Types
The system is designed to be extensible. To add new question types:

1. Update the `Question` model to include the new type
2. Add handling in the admin question creation form
3. Update the quiz interface to display the new question type
4. Add scoring logic for the new type

### Styling Customization
The application uses CSS custom properties (variables) for easy theming:
- Primary colors, fonts, and spacing can be modified in `base.html`
- Bootstrap classes provide consistent responsive design

### Payment Integration
The subscription system is prepared for payment processor integration:
- Stripe configuration is set up in `app.py`
- Subscription models include payment tracking fields
- Frontend includes placeholder for payment forms

## Deployment Considerations

For production deployment:

1. **Environment Variables**: Move sensitive configuration to environment variables
2. **Database**: Consider PostgreSQL or MySQL for production
3. **File Storage**: Use cloud storage (AWS S3, etc.) for uploaded images
4. **Payment Processing**: Integrate with Stripe or other payment processors
5. **Security**: Enable HTTPS and implement additional security measures

## Contributing

This is a demonstration project showcasing a complete exam practice platform. The codebase is designed to be:
- Well-documented and readable
- Modular and extensible
- Following Flask best practices
- Responsive and user-friendly

## Support

For questions about this demo project or suggestions for improvements, please refer to the code comments and documentation throughout the application.

---

**Note**: This is a demonstration/portfolio project. For production use, additional security measures, error handling, and scalability considerations should be implemented.