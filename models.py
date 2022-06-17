from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relation
from sqlalchemy_utils import database_exists, create_database
import bcrypt
from db import Engine, Session
import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    username = Column("username", String(50), primary_key = True)
    email = Column("email", String(50), unique = True, nullable = False)
    password_hash = Column("password_hash", String, nullable = False)
    admin = Column("admin", Boolean, nullable = False)
    moder = Column("moder", Boolean, nullable = False)
    writer = Column("writer", Boolean, nullable = False)
    user = Column("user", Boolean, nullable = False)
    blacklist = Column("blacklist", Boolean, nullable = False)

class Article(Base):
    __tablename__ = "articles"
    
    article_writer_rel = relation("ArticleWriter", cascade = "all, delete") 
    comment_rel = relation("Comment", cascade = "all, delete") 

    article_id = Column("article_id", Integer, primary_key = True)
    header = Column("header", String(50), nullable = False)
    body = Column("body", String(50000), nullable = False)
    state = Column("state", String(50), CheckConstraint("state = 'draft' or state = 'published' or state = 'approved' or state = 'declined'"), nullable = False)
    decline_reason = Column("decline_reason", String(500))

class ArticleWriter(Base):
    __tablename__ = "article_writers"

    article_id = Column("article_id", Integer, ForeignKey("articles.article_id"), primary_key = True)
    username = Column("username", String(50), ForeignKey("users.username"), primary_key = True)
    position = Column("position", String(50), CheckConstraint("position = 'creator' or position = 'author' or position = 'editor'"), nullable = False)

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column("comment_id", Integer, primary_key = True)
    body = Column("body", String(500), nullable = False)
    username = Column("username", String(50), ForeignKey("users.username"), nullable = False)
    article_id = Column("article_id", Integer, ForeignKey("articles.article_id"), nullable = False)

if not database_exists(Engine.url):
    create_database(Engine.url)
    Base.metadata.create_all(Engine)
  
    password = settings.admin["password"]
    password = password.encode("ascii", "strict")
    hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    
    user = User(
            email = settings.admin["email"],
            username = settings.admin["username"],
            password_hash = hash,
            blacklist = False,
            admin = True,
            moder = True,
            writer = True,
            user = True
    )

    session = Session()
    session.add(user)
    session.commit()

 
