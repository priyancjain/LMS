from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import URL

from auth import get_session, require_role
from models import (
    FlowCreateRequest,
    QuestionCreateRequest,
    create_flow,
    create_question,
    get_flow,
    list_flows,
    list_questions_for_flow,
)

router = APIRouter(
    prefix="/teacher",
    tags=["teacher"],
    dependencies=[Depends(require_role("teacher"))],
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _wants_html(request: Request) -> bool:
    return "text/html" in (request.headers.get("accept") or "")


def _redirect_with_message(url: str, message: str, kind: str = "success") -> RedirectResponse:
    target = URL(url).include_query_params(message=message, kind=kind)
    return RedirectResponse(url=str(target), status_code=303)


@router.get("/dashboard")
def teacher_dashboard(request: Request, session: dict = Depends(get_session)):
    payload = {"role": "teacher", "email": session.get("email"), "dashboard": "ok"}
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
    print(f"DEBUG: teacher_dashboard flows count = {len(flows)}")
    for f in flows[:3]:
        print(f"DEBUG: flow = {f.title}")
    
    # Convert dataclass to dict for Jinja2 template compatibility
    flows_dict = [
        {"flow_id": f.flow_id, "title": f.title, "created_by": f.created_by, "created_at": f.created_at}
        for f in flows
    ]
    
    return templates.TemplateResponse(
        "teacher_dashboard.html",
        {
            "request": request,
            "page_title": "Teacher Dashboard",
            "subtitle": "Create flows and add questions.",
            "role": "teacher",
            "user_email": session.get("email"),
            "message": message,
            "message_class": message_class,
            "flows": flows_dict,
        },
    )


@router.post("/flow/create")
def create_learning_flow(request: Request, payload: FlowCreateRequest, session: dict = Depends(get_session)):
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    flow = create_flow(title=title, created_by=session.get("email", ""))
    response_payload = {
        "flow_id": flow.flow_id,
        "title": flow.title,
        "created_by": flow.created_by,
    }
    if _wants_html(request):
        return _redirect_with_message(
            "/teacher/dashboard",
            message=f"Flow created: {flow.title} (ID: {flow.flow_id})",
            kind="success",
        )
    return JSONResponse(response_payload)

@router.post("/ui/flow/create")
def create_learning_flow_ui(title: str = Form(...), session: dict = Depends(get_session)):
    title = title.strip()
    if not title:
        return _redirect_with_message("/teacher/dashboard", message="Title is required.", kind="error")
    flow = create_flow(title=title, created_by=session.get("email", ""))
    return _redirect_with_message(
        "/teacher/dashboard",
        message=f"Flow created: {flow.title} (ID: {flow.flow_id})",
        kind="success",
    )


@router.post("/question/create")
def create_flow_question(request: Request, payload: QuestionCreateRequest):
    flow = get_flow(payload.flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="flow not found")
    if not payload.options:
        raise HTTPException(status_code=400, detail="options must not be empty")
    if payload.correct_answer not in payload.options:
        raise HTTPException(status_code=400, detail="correct_answer must be one of options")

    question = create_question(
        flow_id=payload.flow_id,
        difficulty=payload.difficulty,
        question_text=payload.question_text,
        options=payload.options,
        correct_answer=payload.correct_answer,
        hint_text=payload.hint_text,
    )
    response_payload = {
        "question_id": question.question_id,
        "flow_id": question.flow_id,
        "difficulty": question.difficulty,
        "question_text": question.question_text,
        "options": question.options,
        "correct_answer": question.correct_answer,
        "hint_text": question.hint_text,
    }
    if _wants_html(request):
        return _redirect_with_message(
            "/teacher/dashboard",
            message=f"Question added to flow {question.flow_id} ({question.difficulty}).",
            kind="success",
        )
    return JSONResponse(response_payload)

@router.post("/ui/question/create")
def create_flow_question_ui(
    flow_id: str = Form(...),
    difficulty: str = Form(...),
    question_text: str = Form(...),
    options: str = Form(...),
    correct_answer: str = Form(...),
    hint_text: str = Form(""),
):
    flow_id = flow_id.strip()
    flow = get_flow(flow_id)
    if not flow:
        return _redirect_with_message("/teacher/dashboard", message="Flow not found.", kind="error")

    parsed_options = [o.strip() for o in options.splitlines() if o.strip()]
    if not parsed_options:
        return _redirect_with_message("/teacher/dashboard", message="Options must not be empty.", kind="error")
    correct_answer = correct_answer.strip()
    if correct_answer not in parsed_options:
        return _redirect_with_message(
            "/teacher/dashboard",
            message="Correct answer must match one of the options exactly.",
            kind="error",
        )

    create_question(
        flow_id=flow_id,
        difficulty=difficulty,
        question_text=question_text.strip(),
        options=parsed_options,
        correct_answer=correct_answer,
        hint_text=hint_text.strip(),
    )
    return _redirect_with_message(
        "/teacher/dashboard",
        message=f"Question added to flow {flow_id} ({difficulty}).",
        kind="success",
    )


@router.get("/flow/{flow_id}")
def get_flow_detail(flow_id: str):
    flow = get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="flow not found")
    questions = list_questions_for_flow(flow_id)
    return {
        "flow": {
            "flow_id": flow.flow_id,
            "title": flow.title,
            "created_by": flow.created_by,
        },
        "questions": [
            {
                "question_id": q.question_id,
                "flow_id": q.flow_id,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "hint_text": q.hint_text,
            }
            for q in questions
        ],
    }
