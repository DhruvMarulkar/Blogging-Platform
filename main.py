from fastapi import FastAPI , Request , HTTPException , status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]


@app.get("/",include_in_schema=False,name="home")
@app.get("/posts",include_in_schema=False,name="posts")

def home(request:Request):
    return templates.TemplateResponse("home.html",{"request":request,"posts":posts,"title":"home"},)

@app.get("/posts/{post_id}",include_in_schema=False)
def post_page(request:Request,post_id:int):
    for post in posts:
        if post.get("id") == post_id:
             title = post["title"][:50]
             return templates.TemplateResponse("post.html",{"request":request,"post":post,"title":title},)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")

@app.get("/api/posts")
def get_posts():
    return posts

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request:Request,exception:StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please try again"
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail":message},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code":exception.status_code,
            "title":exception.status_code,
            "message":message,
        },
        status_code=exception.status_code,
    )

@app.exception_handler(RequestValidationError)
def general_http_exception_handler(request:Request,exception:RequestValidationError):

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail":exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message":"Invalid request. Please check input",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT   ,
    )