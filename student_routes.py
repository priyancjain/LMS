from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import time

from auth import get_session, require_role, set_session
from models import get_flow, list_flows, list_questions_for_flow

router = APIRouter(
    prefix="/student",
    tags=["student"],
    dependencies=[Depends(require_role("student"))],
)


@router.get("/dashboard")
def student_dashboard(request: Request, session: dict = Depends(get_session)):
    payload = {"role": "student", "email": session.get("email"), "dashboard": "ok"}
    if not _wants_html(request):
        return payload

    kind = request.query_params.get("kind")
    message = request.query_params.get("message")
    message_class = None
    if kind == "success":
        message_class = "alert-success"
    elif kind == "warn":
        message_class = "alert-warn"
    elif kind == "error":
        message_class = "alert-error"

    flows = list_flows()
    return templates.TemplateResponse(
        "student_dashboard.html",
        {
            "request": request,
            "page_title": "Student Dashboard",
            "subtitle": "Choose a flow and start learning.",
            "role": "student",
            "user_email": session.get("email"),
            "flows": [{"flow_id": f.flow_id, "title": f.title} for f in flows],
            "message": message,
            "message_class": message_class,
        },
    )


class StartFlowRequest(BaseModel):
    flow_id: str


class AnswerRequest(BaseModel):
    flow_id: str
    answer: str


DIFFICULTY_ORDER = ["easy", "medium", "hard"]

SUMMARY_SESSION_KEY = "flow_summary"
COMPLETED_SESSION_KEY = "flow_completed"

FAST_RESPONSE_SECONDS = 5
SLOW_RESPONSE_SECONDS = 20

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _wants_html(request: Request) -> bool:
    return "text/html" in (request.headers.get("accept") or "")


async def _parse_request_data(request: Request) -> dict:
    content_type = (request.headers.get("content-type") or "").lower()
    if content_type.startswith("application/json"):
        data = await request.json()
        return data if isinstance(data, dict) else {}
    form = await request.form()
    return dict(form)


def _init_progress_state(session: dict) -> None:
    session["current_difficulty"] = "easy"
    session["correct_count"] = 0
    session["wrong_count"] = 0
    session["attempts_per_question"] = {}
    session["completed_question_ids"] = []
    session["current_question_id"] = None
    session["total_correct_answers"] = 0
    session.pop("question_started_at", None)
    session.pop(SUMMARY_SESSION_KEY, None)
    session.pop(COMPLETED_SESSION_KEY, None)


def _start_question_timer(session: dict) -> None:
    session["question_started_at"] = time.time()


def _get_response_speed(session: dict) -> tuple[str, float | None]:
    started_at = session.get("question_started_at")
    if not isinstance(started_at, (int, float)):
        return ("normal", None)
    elapsed = max(0.0, time.time() - float(started_at))
    if elapsed <= FAST_RESPONSE_SECONDS:
        return ("fast", elapsed)
    if elapsed >= SLOW_RESPONSE_SECONDS:
        return ("slow", elapsed)
    return ("normal", elapsed)


def _clamp_difficulty(value: str) -> str:
    return value if value in DIFFICULTY_ORDER else "easy"


def _step_difficulty(current: str, direction: int) -> str:
    current = _clamp_difficulty(current)
    idx = DIFFICULTY_ORDER.index(current)
    idx = max(0, min(len(DIFFICULTY_ORDER) - 1, idx + direction))
    return DIFFICULTY_ORDER[idx]


def _select_next_question(questions, preferred_difficulty: str, completed_ids: set, exclude_id: str | None):
    preferred_difficulty = _clamp_difficulty(preferred_difficulty)

    if preferred_difficulty == "easy":
        difficulties = ["easy", "medium", "hard"]
    elif preferred_difficulty == "medium":
        difficulties = ["medium", "easy", "hard"]
    else:
        difficulties = ["hard", "medium", "easy"]

    for difficulty in difficulties:
        for q in questions:
            if q.difficulty != difficulty:
                continue
            if q.question_id in completed_ids:
                continue
            if exclude_id and q.question_id == exclude_id:
                continue
            return q
    return None


def _question_for_student(question):
    return {
        "question_id": question.question_id,
        "flow_id": question.flow_id,
        "difficulty": question.difficulty,
        "question_text": question.question_text,
        "options": question.options,
    }


@router.get("/flows")
def student_flows():
    flows = list_flows()
    return {
        "flows": [
            {"flow_id": f.flow_id, "title": f.title, "created_by": f.created_by}
            for f in flows
        ]
    }


@router.post("/flow/start")
async def start_flow(request: Request, session: dict = Depends(get_session)):
    data = await _parse_request_data(request)
    payload = StartFlowRequest(**data)
    flow = get_flow(payload.flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="flow not found")

    questions = list_questions_for_flow(payload.flow_id)
    if not questions:
        raise HTTPException(status_code=400, detail="flow has no questions")

    session["active_flow_id"] = payload.flow_id
    session["question_index"] = 0
    _init_progress_state(session)

    completed_ids = set(session.get("completed_question_ids") or [])
    first_question = _select_next_question(
        questions,
        preferred_difficulty=session.get("current_difficulty", "easy"),
        completed_ids=completed_ids,
        exclude_id=None,
    )
    if not first_question:
        raise HTTPException(status_code=400, detail="no available questions for this flow")
    session["current_question_id"] = first_question.question_id
    _start_question_timer(session)

    response_payload = {
        "flow": {"flow_id": flow.flow_id, "title": flow.title},
        "progress": {"question_index": 0, "total_questions": len(questions)},
        "question": _question_for_student(first_question),
    }

    if _wants_html(request):
        response = templates.TemplateResponse(
            "question.html",
            {
                "request": request,
                "page_title": "Learning Journey",
                "subtitle": response_payload["flow"]["title"],
                "role": "student",
                "user_email": session.get("email"),
                "progress": response_payload["progress"],
                "question": response_payload["question"],
                "hint": None,
                "feedback": None,
                "feedback_class": None,
                "current_difficulty": session.get("current_difficulty", "easy"),
                "session_state": {
                    "current_difficulty": session.get("current_difficulty", "easy"),
                    "correct_count": int(session.get("correct_count", 0)),
                    "wrong_count": int(session.get("wrong_count", 0)),
                },
            },
        )
    else:
        response = JSONResponse(response_payload)
    set_session(response, session)
    return response


@router.post("/answer")
async def submit_answer(request: Request, session: dict = Depends(get_session)):
    data = await _parse_request_data(request)
    payload = AnswerRequest(**data)
    active_flow_id = session.get("active_flow_id")
    if not active_flow_id:
        raise HTTPException(status_code=400, detail="no active flow; start a flow first")
    if payload.flow_id != active_flow_id:
        raise HTTPException(status_code=400, detail="flow_id does not match active flow")

    questions = list_questions_for_flow(active_flow_id)
    if not questions:
        raise HTTPException(status_code=400, detail="flow has no questions")

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        raise HTTPException(status_code=400, detail="invalid session; restart the flow")
    current = next((q for q in questions if q.question_id == current_question_id), None)
    if not current:
        raise HTTPException(status_code=400, detail="question not found; restart the flow")

    is_correct = payload.answer == current.correct_answer
    response_speed, elapsed_seconds = _get_response_speed(session)

    attempts = session.get("attempts_per_question")
    if not isinstance(attempts, dict):
        attempts = {}
    attempts[current.question_id] = int(attempts.get(current.question_id, 0)) + 1
    session["attempts_per_question"] = attempts

    session["current_difficulty"] = _clamp_difficulty(session.get("current_difficulty", "easy"))
    session["correct_count"] = int(session.get("correct_count", 0))
    session["wrong_count"] = int(session.get("wrong_count", 0))

    hint = None
    prevent_level_up = False
    completed_ids = session.get("completed_question_ids")
    if not isinstance(completed_ids, list):
        completed_ids = []
    completed_id_set = set(completed_ids)

    if is_correct:
        session["wrong_count"] = 0
        if response_speed == "fast":
            session["correct_count"] = int(session.get("correct_count", 0)) + 2
        else:
            session["correct_count"] = int(session.get("correct_count", 0)) + 1
            if response_speed == "slow":
                prevent_level_up = True
        session["total_correct_answers"] = int(session.get("total_correct_answers", 0)) + 1
        session["wrong_count"] = 0
        if current.question_id not in completed_id_set:
            completed_ids.append(current.question_id)
            completed_id_set.add(current.question_id)

        if session["correct_count"] >= 2 and not prevent_level_up:
            session["current_difficulty"] = _step_difficulty(session["current_difficulty"], +1)
            session["correct_count"] = 0
    else:
        session["correct_count"] = 0
        if response_speed == "slow":
            session["wrong_count"] = session["wrong_count"] + 2
        else:
            session["wrong_count"] = session["wrong_count"] + 1

        if session["wrong_count"] == 1:
            _start_question_timer(session)
            response_payload = {
                "correct": False,
                "completed": False,
                "progress": {"question_index": len(completed_id_set), "total_questions": len(questions)},
                "question": _question_for_student(current),
                "session_state": {
                    "current_difficulty": session["current_difficulty"],
                    "correct_count": session["correct_count"],
                    "wrong_count": session["wrong_count"],
                    "attempts_per_question": session.get("attempts_per_question", {}),
                },
            }
            if _wants_html(request):
                response = templates.TemplateResponse(
                    "question.html",
                    {
                        "request": request,
                        "page_title": "Learning Journey",
                        "subtitle": "Try again — you’ve got this.",
                        "role": "student",
                        "user_email": session.get("email"),
                        "progress": response_payload["progress"],
                        "question": response_payload["question"],
                        "hint": None,
                        "feedback": "❌ Not quite, try once more!",
                        "feedback_class": "alert-error",
                        "current_difficulty": response_payload["session_state"]["current_difficulty"],
                        "session_state": response_payload["session_state"],
                    },
                )
            else:
                response = JSONResponse(response_payload)
            set_session(response, session)
            return response

        hint = current.hint_text
        session["current_difficulty"] = _step_difficulty(session["current_difficulty"], -1)
        session["wrong_count"] = 0

    session["completed_question_ids"] = completed_ids
    session["question_index"] = len(completed_id_set)

    if len(completed_id_set) >= len(questions):
        session[COMPLETED_SESSION_KEY] = True
        session[SUMMARY_SESSION_KEY] = {
            "total_questions_attempted": len(session.get("attempts_per_question", {})),
            "total_correct_answers": int(session.get("total_correct_answers", 0)),
            "final_difficulty_reached": session.get("current_difficulty", "easy"),
        }
        final_state = {
            "current_difficulty": session.get("current_difficulty", "easy"),
            "correct_count": int(session.get("correct_count", 0)),
            "wrong_count": int(session.get("wrong_count", 0)),
            "attempts_per_question": session.get("attempts_per_question", {}),
        }
        session.pop("active_flow_id", None)
        session.pop("question_index", None)
        session.pop("current_question_id", None)
        session.pop("completed_question_ids", None)
        session.pop("current_difficulty", None)
        session.pop("correct_count", None)
        session.pop("wrong_count", None)
        session.pop("attempts_per_question", None)
        session.pop("total_correct_answers", None)
        session.pop("question_started_at", None)
        response_payload = {
            "correct": is_correct,
            "completed": True,
            "progress": {"question_index": len(questions), "total_questions": len(questions)},
            "session_state": final_state,
        }
        if hint is not None:
            response_payload["hint"] = hint
        if _wants_html(request):
            response = RedirectResponse(url="/student/summary", status_code=303)
        else:
            response = JSONResponse(response_payload)
        set_session(response, session)
        return response

    next_question = _select_next_question(
        questions,
        preferred_difficulty=session.get("current_difficulty", "easy"),
        completed_ids=completed_id_set,
        exclude_id=current.question_id,
    )
    if not next_question:
        session[COMPLETED_SESSION_KEY] = True
        session[SUMMARY_SESSION_KEY] = {
            "total_questions_attempted": len(session.get("attempts_per_question", {})),
            "total_correct_answers": int(session.get("total_correct_answers", 0)),
            "final_difficulty_reached": session.get("current_difficulty", "easy"),
        }
        session.pop("question_started_at", None)
        response_payload = {
            "correct": is_correct,
            "completed": True,
            "progress": {"question_index": len(questions), "total_questions": len(questions)},
            "session_state": {
                "current_difficulty": session.get("current_difficulty", "easy"),
                "correct_count": int(session.get("correct_count", 0)),
                "wrong_count": int(session.get("wrong_count", 0)),
                "attempts_per_question": session.get("attempts_per_question", {}),
            },
        }
        if hint is not None:
            response_payload["hint"] = hint
        if _wants_html(request):
            response = RedirectResponse(url="/student/summary", status_code=303)
        else:
            response = JSONResponse(response_payload)
        set_session(response, session)
        return response

    session["current_question_id"] = next_question.question_id
    _start_question_timer(session)
    response_payload = {
        "correct": is_correct,
        "completed": False,
        "progress": {"question_index": len(completed_id_set), "total_questions": len(questions)},
        "question": _question_for_student(next_question),
        "session_state": {
            "current_difficulty": session.get("current_difficulty", "easy"),
            "correct_count": int(session.get("correct_count", 0)),
            "wrong_count": int(session.get("wrong_count", 0)),
            "attempts_per_question": session.get("attempts_per_question", {}),
        },
    }
    if hint is not None:
        response_payload["hint"] = hint
    if _wants_html(request):
        feedback = "✅ Nice work! Let’s keep going 🚀" if is_correct else "❌ Not quite, try once more!"
        feedback_class = "alert-success" if is_correct else "alert-error"
        if not is_correct and hint is not None:
            feedback = "❌ Two tries — here’s a hint, and we’ll adjust the level."
            feedback_class = "alert-warn"

        response = templates.TemplateResponse(
            "question.html",
            {
                "request": request,
                "page_title": "Learning Journey",
                "subtitle": "The level adapts based on your performance.",
                "role": "student",
                "user_email": session.get("email"),
                "progress": response_payload["progress"],
                "question": response_payload["question"],
                "hint": response_payload.get("hint"),
                "feedback": feedback,
                "feedback_class": feedback_class,
                "current_difficulty": response_payload["session_state"]["current_difficulty"],
                "session_state": response_payload["session_state"],
            },
        )
    else:
        response = JSONResponse(response_payload)
    set_session(response, session)
    return response


@router.get("/summary")
def student_summary(request: Request, session: dict = Depends(get_session)):
    summary = session.get(SUMMARY_SESSION_KEY)
    completed = bool(session.get(COMPLETED_SESSION_KEY))
    if not completed or not summary:
        if _wants_html(request):
            return templates.TemplateResponse(
                "summary.html",
                {
                    "request": request,
                    "page_title": "Summary",
                    "subtitle": "Finish a flow to see your results.",
                    "role": "student",
                    "user_email": session.get("email"),
                    "summary": None,
                    "message": "Flow not completed yet. Start a journey first.",
                },
                status_code=400,
            )
        raise HTTPException(status_code=400, detail="Flow not completed yet")

    if _wants_html(request):
        return templates.TemplateResponse(
            "summary.html",
            {
                "request": request,
                "page_title": "Summary",
                "subtitle": "You did it — here are your results.",
                "role": "student",
                "user_email": session.get("email"),
                "summary": summary,
                "message": None,
            },
        )
    return summary
