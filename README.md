# Exam Practice Hub

A comprehensive exam practice website designed for school children to improve their academic performance through interactive quizzes and practice tests.

## Features

### 🎯 Core Features
- **Multi-Subject Support**: Practice across various subjects with customizable content
- **Year Group Categorization**: Questions tailored to specific academic year levels (7-13)
- **Complexity Levels**: Three difficulty levels (Low, Medium, High) for adaptive learning
- **Question Types**: Support for multiple choice and short answer questions
- **Image Support**: Questions and answers can include images for enhanced learning
- **Subscription Management**: Free trial with time-based subscription options

### 👨‍🎓 Student Features
- **User Registration & Login**: Secure account creation with automatic 7-day free trial
- **Interactive Quizzes**: Timed quizzes with progress tracking and auto-save
- **Performance Analytics**: Detailed score analysis with personalized recommendations
- **Achievement System**: Unlock achievements for high performance
- **Progress Tracking**: View quiz history and performance trends
- **Subscription Plans**: Flexible monthly and yearly subscription options

### 👨‍💼 Admin Features
- **Question Bank Management**: Add, edit, and organize questions with rich content
- **Subject Management**: Create and manage subject categories
- **Quiz Generation**: Automatically generate quizzes based on criteria
- **User Analytics**: View platform statistics and user metrics
- **Content Control**: Full control over question complexity and categorization

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Authentication**: Werkzeug password hashing
- **File Upload**: Secure image handling with UUID naming
- **Responsive Design**: Mobile-first responsive interface

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd exam-practice-hub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Register a new student account or use admin credentials below

### Default Admin Credentials
- **Username**: admin
- **Password**: admin123

## Application Structure

```
exam-practice-hub/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── uploads/          # Uploaded images
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   ├── subscription.html
│   ├── take_quiz.html
│   ├── quiz_results.html
│   ├── manage_subjects.html
│   ├── manage_questions.html
│   ├── add_question.html
│   └── create_quiz.html
└── exam_practice.db     # SQLite database (created automatically)
```

## Database Schema

### Users
- User authentication and profile information
- Role-based access (student/admin)
- Year group assignment

### Subscriptions
- Time-based subscription management
- Free trial support
- Multiple subscription types

### Subjects
- Subject categorization
- Description and metadata

### Questions
- Rich question content with image support
- Multiple choice and short answer types
- Complexity and year group targeting
- Correct answer storage

### Quizzes
- Generated quiz management
- Question association
- Performance tracking

### Quiz Attempts
- Student quiz results
- Score tracking and analytics

## Key Features Explained

### Subscription System
- **Free Trial**: 7-day trial for new users
- **Monthly Plan**: $9.99/month with full access
- **Yearly Plan**: $99.99/year (17% savings)
- Automatic expiration handling with grace period

### Question Bank
- Support for text and image questions
- Multiple choice with 4 options (A, B, C, D)
- Short answer with reference materials
- Complexity tagging for adaptive difficulty

### Quiz Generation
- Automatic question selection based on criteria
- Random sampling for variety
- Subject, year group, and complexity filtering
- Customizable quiz length (5-30 questions)

### Performance Analytics
- Percentage-based scoring
- Performance categorization (Outstanding, Excellent, Good, Fair, Needs Improvement)
- Personalized recommendations
- Achievement unlocks for high scores

## Usage Guide

### For Students

1. **Registration**
   - Sign up with username, email, and year group
   - Receive automatic 7-day free trial
   - Access all subjects and features

2. **Taking Quizzes**
   - Select subject from dashboard
   - Choose difficulty level and number of questions
   - Complete timed quiz with progress tracking
   - View detailed results and recommendations

3. **Managing Subscription**
   - Monitor trial/subscription status
   - Upgrade to monthly or yearly plans
   - Access subscription management page

### For Administrators

1. **Subject Management**
   - Add new subjects with descriptions
   - Organize content by academic areas
   - View subject statistics

2. **Question Bank**
   - Add questions with rich content (text + images)
   - Set appropriate complexity levels
   - Categorize by subject and year group
   - Support multiple question types

3. **Quiz Creation**
   - Generate quizzes automatically
   - Set criteria for question selection
   - Create balanced assessments

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- File upload validation and sanitization
- SQL injection prevention through ORM
- XSS protection through template escaping

## Customization Options

### Adding New Subjects
1. Log in as admin
2. Navigate to "Manage Subjects"
3. Add subject name and description
4. Start adding questions for the subject

### Modifying Subscription Plans
- Update pricing in `templates/subscription.html`
- Modify subscription logic in `app.py`
- Adjust trial periods and durations as needed

### Styling Customization
- Modify `static/css/style.css` for visual changes
- Update color schemes and branding
- Customize component styles

## Performance Considerations

- **Database Optimization**: Indexed foreign keys for fast queries
- **Image Handling**: UUID-based naming prevents conflicts
- **Pagination**: Question lists paginated for performance
- **Session Management**: Efficient session handling
- **Responsive Design**: Optimized for all device sizes

## Future Enhancements

- [ ] Advanced analytics dashboard
- [ ] Bulk question import (CSV/Excel)
- [ ] Question difficulty auto-adjustment based on performance
- [ ] Study groups and collaborative features
- [ ] Mobile app development
- [ ] Integration with payment gateways
- [ ] Multi-language support
- [ ] Advanced search and filtering
- [ ] Question categorization by topics
- [ ] Timed practice modes

## Troubleshooting

### Common Issues

1. **Database not found**
   - Run the application once to create the database automatically
   - Check file permissions in the project directory

2. **Images not displaying**
   - Ensure the `static/uploads/` directory exists
   - Check file permissions for uploaded images

3. **Admin access issues**
   - Use default credentials: admin/admin123
   - Admin user is created automatically on first run

4. **Subscription not working**
   - Check database entries for subscription table
   - Verify date calculations in subscription logic

### Development Mode
Run with debug enabled:
```bash
export FLASK_ENV=development
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository.

---

**Exam Practice Hub** - Empowering students through interactive learning and practice.