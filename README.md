# Adaptive Learning System

A modern, intelligent learning management system powered by adaptive algorithms. Students learn at their own pace with difficulty levels that adjust based on their performance in real-time.

## Features

- **Google Authentication** - Secure OAuth 2.0 login
- **Dual Role System** - Teacher and Student interfaces
- **Smart Adaptive Learning** 
  - Dynamic difficulty progression (Easy → Medium → Hard)
  - Auto level-up after 2 consecutive correct answers
  - Auto level-down after 2 wrong answers
  - Intelligent hint system
  - Speed-based performance scoring
- **Learning Flow Management** - Teachers create custom learning flows with multiple questions
- **Real-time Progress Tracking** - Live progress metrics and performance analytics
- **Secure Session Management** - JWT-like token-based authentication

## Tech Stack

- **Backend**: FastAPI + Uvicorn (Python 3.11)
- **Database**: SQLite
- **Frontend**: Jinja2 Templates + HTML/CSS
- **Authentication**: Google OAuth 2.0

## Project Structure

```
poc/
├── main.py                 # FastAPI application entry point
├── auth.py                 # Google OAuth authentication
├── models.py               # Database models and CRUD operations
├── teacher_routes.py       # Teacher endpoints and logic
├── student_routes.py       # Student endpoints and adaptive learning
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── home.html
│   ├── question.html
│   ├── student_dashboard.html
│   ├── teacher_dashboard.html
│   └── summary.html
├── static/                 # CSS and static assets
│   └── style.css
├── seed_flow.py            # Sample data generator
└── poc.db                  # SQLite database
```

## Setup & Installation

### Prerequisites
- Python 3.11+
- pip and virtualenv

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/priyancjain/LMS.git
   cd LMS
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google OAuth credentials
   ```

5. **Initialize database**
   ```bash
   python -c "from models import init_db; init_db()"
   ```

6. **Run the server**
   ```bash
   python -m uvicorn main:app --reload
   ```

7. **Access the application**
   ```
   http://localhost:8000
   ```

## Usage

### For Teachers
1. Log in with Google
2. Go to Teacher Dashboard
3. Create a new learning flow
4. Add questions with different difficulty levels
5. View all flows and manage content

### For Students
1. Log in with Google
2. Go to Student Dashboard
3. Select a learning flow to begin
4. Answer questions and adapt to changing difficulty
5. View performance summary upon completion

## Adaptive Learning Algorithm

The system implements a sophisticated adaptive learning algorithm:

- **Difficulty Progression**: Students start at EASY level
- **Level Up Condition**: 2 consecutive correct answers → advance to next difficulty
- **Level Down Condition**: 2 wrong answers → regress to previous difficulty
- **Speed Bonus**: Fast answers (< 5 sec) award +2 points instead of +1
- **Slow Penalty**: Slow answers (> 20 sec) prevent level up
- **Hint System**: Provided after first wrong answer to help students

## Testing

The system has been thoroughly tested with multiple flows and questions:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload

# Access at http://localhost:8000
```

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET /login/google` - Google login redirect
- `GET /auth/callback` - OAuth callback

### Teacher Routes
- `GET /teacher/dashboard` - Teacher dashboard
- `POST /teacher/flow/create` - Create new flow
- `POST /teacher/question/create` - Add question to flow
- `POST /teacher/ui/flow/create` - UI form submission

### Student Routes
- `GET /student/dashboard` - Student dashboard
- `GET /student/flows` - List all available flows
- `POST /student/flow/start` - Start a learning flow
- `POST /student/answer` - Submit answer

## Environment Variables

Required `.env` file:
```
SESSION_SECRET=your_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Performance Metrics

The system tracks:
- Current difficulty level reached
- Number of correct/wrong answers
- Response time for each question
- Attempts per question
- Total questions attempted
- Final difficulty achieved

## Known Limitations

- SQLite for development (recommend PostgreSQL for production)
- Single-server deployment
- Session data stored in cookies (upgrade to database persistence for production)

## Future Enhancements

- [ ] Personalized recommendations engine
- [ ] Advanced analytics dashboard
- [ ] AI-powered question generation
- [ ] Mobile application
- [ ] Real-time collaboration features
- [ ] Multi-language support
- [ ] Assessment and certification system

## Deployment

Deploy to Render, Heroku, AWS, or any cloud provider supporting Python:

1. Set environment variables (SESSION_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
2. Configure database (PostgreSQL recommended for production)
3. Use provided `render.yaml` for Render deployment
4. Use `Procfile` for Heroku deployment

See deployment configuration files for detailed setup.

## Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## License

MIT License - See LICENSE file for details

## Support

For questions, issues, or suggestions, please open an issue on GitHub.
