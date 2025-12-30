# Adaptive Learning System POC

An AI-powered adaptive learning platform built with Python and FastAPI. Students progress through difficulties dynamically based on their performance.

## Features

- **Google Authentication** - Secure login with Google OAuth 2.0
- **Dual Role System** - Separate interfaces for Teachers and Students
- **Adaptive Learning Algorithm** - Dynamic difficulty progression based on performance
  - 3 difficulty levels (Easy → Medium → Hard)
  - Auto level-up after 2 correct answers
  - Auto level-down after 2 wrong answers
  - Speed-based scoring (fast answers = +2 points)
  - Hint system after first wrong answer
- **Flow Management** - Teachers create custom learning flows
- **Progress Tracking** - Real-time progress and performance metrics
- **Session Management** - Secure JWT-like token-based sessions

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite
- **Frontend**: Jinja2 Templates + HTML/CSS
- **Authentication**: Google OAuth 2.0
- **Language**: Python 3.11

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

Run the test scripts to verify functionality:

```bash
# Test flow creation and questions
python -c "exec(open('test_flow.py').read())"

# Test adaptive learning algorithm
python -c "exec(open('test_adaptive.py').read())"

# Create sample data
python -c "from seed_flow import *"
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

- SQLite for POC (not production-ready)
- Single-server deployment
- No real-time collaboration
- Session data stored in cookies (no database persistence)

## Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] AI-powered question generation
- [ ] Mobile application
- [ ] Multiplayer learning modes
- [ ] Real-time progress notifications

## Deployment

To deploy:

1. Choose hosting platform (Heroku, Railway, Vercel, AWS, etc.)
2. Set environment variables
3. Configure database (upgrade to PostgreSQL for production)
4. Deploy using platform-specific instructions

## Contributing

This is a POC project. All code and assets created remain 100% yours.

## License

MIT License

## Support

For questions or issues, reach out to the development team.
