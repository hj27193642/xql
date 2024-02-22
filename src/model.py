from sqlalchemy import create_engine, Column, Integer, String, Text, Sequence, Boolean, SmallInteger, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from database import Session, Base, engine, BASE_MODELS
from pydantic import condecimal, BaseModel
import graphene

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


UnsignedInt = Integer()
UnsignedInt = UnsignedInt.with_variant(INTEGER(unsigned=True), 'mysql')


"""
 * @brief Dynamic Models >> data type def
 * 
 * @note 
 * @see model.dynamic_models
"""
def colType (tp='int', types=False ):
	if tp == "int":
		return Integer
	elif tp == "unsignedInt":
		return UnsignedInt
	elif tp == "smallInt":
		return SmallInteger
	elif tp == "tinyInt":
		return TINYINT
	elif tp == "varchar" or tp == "email":
		if types == 0 or types == False: 
			types = 20
		return String(types)
	elif tp == "text":
		return Text
	elif tp == "mediumtext":
		return Text(64000)
	elif tp == "longtext":
		return Text(4294000000)



"""
 * @brief Dynamic Models >> JSON >> data type def
 * 
 * @note 
 * @see 
"""
def jsonType (tp='int'):
	if tp == "int":
		return graphene.Int()
	elif tp == "str":
		return graphene.String()
	elif tp == "float":
		return graphene.Float()



## @brief Dynamic Models >> JSON
"""
 * @note 
 * @see 
 *
 * class SubdataType(graphene.ObjectType):
 *	key1 = graphene.String()
 *	key2 = graphene.Int()
 *
 * class SubdataInput(graphene.InputObjectType):
 *	...
"""
def dynamic_json_models ( classNm='', objtype='Obj', jsonSets={} ) :
	argX = {}
	for key, jsonData in jsonSets.items():
		argX[key] = jsonType(jsonData)

	if objtype == 'InObj' :
		return type (classNm+(objtype), ( graphene.InputObjectType,  ), argX)
	else :
		return type (classNm+(objtype), ( graphene.ObjectType,  ), argX)



## @brief Dynamic Models (classNmModel)
"""
 * @params string classNm (camel case style)
 *
 * @note base design >> type(class name, args, {})
"""
def dynamic_models( classNm='', dataSets={} ) :
	comment = ''
	if dataSets.get('comment') is not None:
		comment = dataSets['comment']

	# @note Set Arguments
	baseArgs = {
		'__tablename__' : dataSets['table'] 
		,'__table_args__' : {
			'mysql_engine': 'InnoDB'
			,'comment': comment
    }
		
	}
	if dataSets.get('foreignKeys') is not None and 'Partners' in dataSets['foreignKeys']:
		baseArgs['partner_idx'] = Column(UnsignedInt, index=True, nullable=False, default=1)
		# @option ForeignKey("partners.idx"), 
	
	if dataSets.get('foreignKeys') is not None and 'Users' in dataSets['foreignKeys']:
		baseArgs['users_idx'] = Column(UnsignedInt, index=True, nullable=False, default=1)
		# @option ForeignKey("users.idx"), 

	baseArgs['idx'] = Column(UnsignedInt, primary_key=True, nullable=False, default=None, autoincrement=True)
	baseArgs['is_active'] = Column(TINYINT, index=True, nullable=False, default=1,comment="0:deactive 1:active")
	baseArgs['create_date'] = Column(UnsignedInt, nullable=False, default=0)
	baseArgs['update_date'] = Column(UnsignedInt, index=True, nullable=False, default=0)
	for colNm, colData in dataSets['columns'].items():
		idxValue = False
		nullValue = False
		comments = ''
		if 'index' in colData:
			idxValue = colData['index']
		if 'null' in colData:
			nullValue = colData['null']
		if 'val' in colData :
			colData['val'] = 0
		if 'comment' in colData:
			comments = colData['comment']
		
		baseArgs[colNm] = Column(colType(colData['type'], colData['val'] ), index=idxValue, nullable=nullValue, comment=comments )

	return type(classNm+'Model', (Base, ), baseArgs)



## @brief BASE MODEL
if BASE_MODELS == True :
	## @brief Consumer Service model
	"""
	 * @params string classNm
	 *
	 * @note .env Turn on BASE_MODELS 
	"""
	class PartnersModel(Base):
		__tablename__ = "partners"
		__table_args__= {
				'mysql_engine': 'InnoDB'
				,'comment': "Partner Service"
			}
		idx = Column(UnsignedInt, primary_key=True, nullable=False, autoincrement=True)
		is_active = Column(TINYINT, index=True, nullable=False, default=1,comment="0:deactive 1:active")
		create_date = Column(UnsignedInt, nullable=False, default=0)
		update_date = Column(UnsignedInt, nullable=False, default=0)
		users_idx = Column(UnsignedInt, index=True, nullable=False, default=0, comment="Users Fkey"  )
		site_id = Column(String(30), index=True, nullable=False, comment="users site id" )
		domain = Column(String(50), index=True, nullable=False, comment="linked Domain" )


	## @brief User Model
	"""
	 * @params string classNm (camel case style )
	 *
	 * @note .env Turn on BASE_MODELS 
	"""
	class UsersModel(Base):
		__tablename__ = "users"
		__table_args__= {
				'mysql_engine': 'InnoDB'
				,'comment': "Users base data"
			}
		partners_idx = Column(UnsignedInt, index=True, nullable=False, default=0, comment="Partners Fkey"  ) #ForeignKey("partners.idx"),
		idx = Column(UnsignedInt, primary_key=True, nullable=False, autoincrement=True, comment="PKEY")
		is_active = Column(TINYINT, index=True, nullable=False, default=1,comment="0:deactive 1:active")
		create_date = Column(UnsignedInt, nullable=False, default=0)
		update_date = Column(UnsignedInt, nullable=False, default=0)
		userid = Column(String(50), index=True, nullable=False, comment="email" )
		passwd = Column(String(255), index=True, nullable=False, comment="passwd" )
		level = Column(String(50), index=True, nullable=False, comment="email" )
		counter = Column(UnsignedInt, nullable=False, default=0, comment="connection count")


class Token(BaseModel):
	access_token: str
	msg : str
