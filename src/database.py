from os import environ
from dotenv.main import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base 
# backref, relationship,

"""
 * @package xql API
 * @author Hyojong hj27193642@gmail.com / cpo@koism.com
 *
 * @date 2024-01-14
 * @see resolver
 *
 * @recent
 * 2023-01-25 MVC repackage
 * 2024-01-14 start project
"""


## @brief MYSQL/MARIADB Connection
"""
 * @note load .env  >> create engine >> make session >> declarative Base 
"""
load_dotenv()
SECRET_KEY = environ['SECRET_KEY']
ALGORITHM = environ['ALGORITHM']
RELOAD_DIRS = environ['RELOAD_DIR']
JSON_MODELS = environ['JSON_MODEL']
BASE_MODELS = True if environ['BASE_MODEL'] == "True" else False
MASTERID = environ['MASTERID']
MASTERPW = environ['MASTERPW']
EXPIRE_TIME = int(environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
DB_CONN_URL = '{}://{}:{}@{}:{}/{}'.format(environ['DB_TYPE'],environ['DB_USER'],environ['DB_PASSWD'],environ['DB_HOST'],environ['DB_PORT'],environ['DB_NAME'],
)
# @option , echo=True, echo_pool="infor"
engine = create_engine(DB_CONN_URL)
Session = sessionmaker(engine)

Base = declarative_base()