from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
import bcrypt
from db import Engine, Session

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key = True)
    email = Column("email", String(50), unique = True, nullable = False)
    username = Column("username", String(50), unique = True, nullable = False)
    password_hash = Column("password_hash", String, nullable = False)
    blacklist = Column("blacklist", Boolean, nullable = False)
    admin_role = Column("admin_role", Boolean, nullable = False)
    moder_role = Column("moder_role", Boolean, nullable = False)
    writer_role = Column("writer_role", Boolean, nullable = False)
    user_role = Column("user_role", Boolean, nullable = False)

class Article(Base):
    __tablename__ = "articles"
    
    id = Column("id", Integer, primary_key = True)
    creator_id = Column("creator_id", Integer, ForeignKey("users.id"), nullable = False)
    header = Column("header", String(50), nullable = False)
    body = Column("body", String(50000), nullable = False)
    state = Column("state", String(50), nullable = False)
    decline_reason = Column("decline_reason", String(500))

class ArticleAuthor(Base):
    __tablename__ = "article_authors"

    article_id = Column("article_id", Integer, ForeignKey("articles.id"), primary_key = True)
    author_id = Column("author_id", Integer, ForeignKey("users.id"), primary_key = True)

class ArticleEditor(Base):
    __tablename__ = "article_editors"

    article_id = Column("article_id", Integer, ForeignKey("articles.id"), primary_key = True)
    editor_id = Column("editor_id", Integer, ForeignKey("users.id"), primary_key = True)

class Comment(Base):
    __tablename__ = "comments"

    id = Column("id", Integer, primary_key = True)
    body = Column("body", String(500), nullable = False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable = False)
    article_id = Column("article_id", Integer, ForeignKey("articles.id"), nullable = False)

if not database_exists(Engine.url):
    create_database(Engine.url)
    Base.metadata.create_all(Engine)
  
    password = "superuser"
    password = password.encode("ascii", "strict")
    hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    
    user = User(
            email = "super@user.com",
            username = "superuser",
            password_hash = hash,
            blacklist = False,
            admin_role = True,
            moder_role = True,
            writer_role = True,
            user_role = True
    )

    session = Session()
    session.add(user)
    session.commit()

 
