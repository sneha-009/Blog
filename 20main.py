from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session
)

# ==========================================
# DATABASE SETUP
# ==========================================

engine = create_engine(
    "sqlite:///final_app.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass


# ==========================================
# BLOG TABLE
# ==========================================

class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(2000))
    author: Mapped[str] = mapped_column(String(100), default="")


Base.metadata.create_all(bind=engine)

# ==========================================
# FASTAPI SETUP
# ==========================================

app = FastAPI()

templates = Jinja2Templates(directory="Frontend")

app.mount(
    "/static",
    StaticFiles(directory="Frontend/static"),
    name="static"
)

# ==========================================
# DATABASE SESSION
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# HOME PAGE
# ==========================================

@app.get("/")
def home():
    return RedirectResponse("/blog", status_code=303)


# ==========================================
# READ ALL BLOGS
# ==========================================

@app.get("/blog", response_class=HTMLResponse)
def blog_index(
    request: Request,
    db: Session = Depends(get_db)
):
    posts = db.scalars(select(Blog)).all()

    return templates.TemplateResponse(
        request=request,
        name="blog_index.html",
        context={"posts": posts}
    )


# ==========================================
# CREATE PAGE
# ==========================================

@app.get("/blog/create", response_class=HTMLResponse)
def blog_create_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="blog_create.html"
    )


# ==========================================
# CREATE BLOG
# ==========================================

@app.post("/blog/create")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(""),
    db: Session = Depends(get_db)
):

    new_post = Blog(
        title=title,
        content=content,
        author=author
    )

    db.add(new_post)
    db.commit()

    return RedirectResponse(
        url="/blog",
        status_code=303
    )


# ==========================================
# VIEW SINGLE BLOG
# ==========================================

@app.get("/blog/{post_id}", response_class=HTMLResponse)
def blog_detail(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):

    post = db.get(Blog, post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="blog_detail.html",
        context={"post": post}
    )


# ==========================================
# UPDATE PAGE
# ==========================================

@app.get("/blog/update/{post_id}", response_class=HTMLResponse)
def blog_update_page(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):

    post = db.get(Blog, post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="blog_update.html",
        context={"post": post}
    )


# ==========================================
# UPDATE BLOG
# ==========================================

@app.post("/blog/update/{post_id}")
def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(""),
    db: Session = Depends(get_db)
):

    post = db.get(Blog, post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    post.title = title
    post.content = content
    post.author = author

    db.commit()

    return RedirectResponse(
        url="/blog",
        status_code=303
    )


# ==========================================
# DELETE BLOG
# ==========================================

@app.post("/blog/delete/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db)
):

    post = db.get(Blog, post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Blog post not found"
        )

    db.delete(post)
    db.commit()

    return RedirectResponse(
        url="/blog",
        status_code=303
    )