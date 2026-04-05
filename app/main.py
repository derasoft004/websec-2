from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import ssau_parser

DEFAULT_GROUP = 1282690301

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/schedule")
async def get_schedule(
    groupId: int = Query(None),
    staffId: int = Query(None),
    week: int = Query(None),
):
    gid = groupId or DEFAULT_GROUP
    if not gid and not staffId:
        return {"error": "groupId or staffId required"}
    try:
        return ssau_parser.fetch_schedule(group_id=gid, staff_id=staffId, week=week)
    except Exception as e:
        return {"error": str(e)}
