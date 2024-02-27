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
		baseArgs['partners_idx'] = Column(UnsignedInt, index=True, nullable=False, server_default="0", comment="Partners Fkey")
	
	if dataSets.get('foreignKeys') is not None and 'Users' in dataSets['foreignKeys']:
		baseArgs['users_idx'] = Column(UnsignedInt, index=True, nullable=False, server_default="1")
		# @option ForeignKey("users.idx"), 
	
	baseArgs['idx'] = Column(UnsignedInt, primary_key=True, nullable=False, server_default="0", autoincrement=True)
	baseArgs['is_active'] = Column(TINYINT, index=True, nullable=False, server_default="1",comment="0:deactive 1:active")
	baseArgs['create_date'] = Column(UnsignedInt, nullable=False, server_default="0")
	baseArgs['update_date'] = Column(UnsignedInt, index=True, nullable=False, server_default="0")
	for colNm, colData in dataSets['columns'].items():
		vargs = {
			"index" : False
			,"nullable" : False
			,"comment" : ""
			,"server_default" : None
		}

		if colData.get('default') is not None and 'default' in colData:
			vargs['server_default'] = str(colData['default'])
		if colData.get('comment') is not None and 'comment' in colData:
			vargs['comment'] = colData['comment']
		if colData.get('index') is not None and 'index' in colData:
			vargs['index'] = colData['index']
		if colData.get('null') is not None and 'null' in colData:
			vargs['nullable'] = colData['null']
		if colData.get('val') is None :
			colData['val'] = 0

		baseArgs[colNm] = Column(colType(colData['type'], colData['val'] ),  **vargs )

	return type(classNm+'Model', (Base, ), baseArgs)



## @brief BASE MODEL
usersPartnersModel = {
	"Partners" : {
		"table" : "partners"
		,"comment": "Partner Service"
		,"columns" : {
			"users_idx" : { "type":"unsignedInt", "index": True ,"comment": "Users Fkey", "default": 1}
			, "site_id" : { "type":"varchar","val":30, "index":True , "comment": "users site id"}
			,"domain" : { "type":"varchar","val":30, "index":True , "comment": "linked Domain"}
		}
	}
	,"Users" : {
		"table" : "users"
		,"comment": "Users base data"
		,"columns" : {
			"userid" : { "type":"email", "val":50, "index":True , "comment": "email"}
			,"user_name" : {"type":"varchar", "val":20, "index":True , "comment": "user name"} 
			,"passwd" : {"type":"varchar", "val":255, "index":True , "comment": "password SHA-512"} 
			,"level" : {"type":"tinyInt", "val":3, "index":True , "comment": "user Level"} 
			,"counter" : {"type":"unsignedInt", "val":11, "index":True , "comment": "connection count"} 
		}
		, "foreignKeys" : ["Partners"]
	}
}




class Token(BaseModel):
	access_token: str
	msg : str
