from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import db_server

server_url = db_server["server"] + "://" + db_server["user"] + ":" + db_server["password"] + "@" + db_server["host"] + ":" + db_server["port"] + "/" + db_server["dbname"]
Engine = create_engine(server_url, echo = True)
Session = sessionmaker(bind = Engine)

