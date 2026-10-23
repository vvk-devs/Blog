from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models,schemas
from auth import verify_access_token,create_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#login api
@app.post("/login")
def login():
    return {
        "access_token": create_access_token({"user": "admin"}),
        "token_type": "Bearer"
    }

@app.get("/")
def home():
    return {"message": "Welcome to the Blog API!"}


#creeate blog
@app.post("/blogs", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db),user = Depends(verify_access_token)):
    new_blog = models.Blog(
        title=blog.title,
        content=blog.content
        )
    
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog


#read all blogs
@app.get("/blogs", response_model=list[schemas.BlogResponse])
def get_blosgs(db:Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

#read blog by id
@app.get("/blogs/{blog_id}", response_model=schemas.BlogResponse)
def get_blog(blog_id:int, db:Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")
    return blog


#update blog
@app.put("/blogs/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(blog_id:int, blog:schemas.BlogCreate, db:Session = Depends(get_db),user = Depends(verify_access_token)):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()

    if not existing_blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")

    existing_blog.title = blog.title
    existing_blog.content = blog.content

    db.commit()
    db.refresh(existing_blog)

    return existing_blog

#blog delete
@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id:int, db:Session = Depends(get_db),delete_user = Depends(verify_access_token)):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()

    if not existing_blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")

    db.delete(existing_blog)
    db.commit()

    return {"message": f"Blog with id {blog_id} has been deleted"}