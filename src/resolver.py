import graphene
from typing import Optional, List, Union, Dict
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from database import Session, Base, engine, JSON_MODELS, SECRET_KEY, ALGORITHM, EXPIRE_TIME, MASTERID, MASTERPW, MASTERNAME

from utility import logX, camelToSnake, Xcrypt, create_access_token, get_hash, hash_password
from time import time 
from datetime import datetime, timedelta
import re
import json
import math
from sqlalchemy import or_, and_


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


## @breif crypt decode/encode Create *
xc = Xcrypt()

type_str_ = ['text', 'varchar', 'mediumtext', 'longtext']
type_int_ = ['int', 'unsignedInt',  'smallInt', 'tinyInt']
type_float_ = ['float', 'double']
type_date_ = ['datetime', 'date']
type_email_ = ['email']



## @brief Email custom scalar
"""
 * @params string classNm (camel case style)
"""
class Email(graphene.Scalar):
	@staticmethod
	def serialize(email):
		# Serialize email to a string
		return str(email)

	@staticmethod
	def parse_value(email):
		# Validate and parse email during input
		if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
			raise ValueError("Invalid email format")
		return email

	@classmethod
	def parse_literal(cls, ast):
		# Parse email from GraphQL literal
		if not isinstance(ast, StringValue):
			raise ValueError("Invalid email format")
		if not re.match(r"[^@]+@[^@]+\.[^@]+", ast.value):
			raise ValueError("Invalid email format")
		return ast.value



## @brief Args def
"""
 * @params string classNm (camel case style)
 * @note 
 *
 * @see schema.dynamic_mutation
"""
def getGrapheneScalarsArgs (cols):
	results = {
		"idx" : graphene.String()
	}
	for key,col in cols.items():
		if col['type'] in type_str_ :
			results[key] = graphene.String()
		elif col['type'] in type_email_ :
			results[key] = graphene.Email()
		elif col['type'] in type_int_ :
			results[key] = graphene.Int()
		elif col['type'] in type_date_ :
			results[key] = graphene.Date()
		elif col['type'] in type_float_ :
			results[key] = graphene.Float()

	return results



## @brief Graphene Entity ( classNmObjType )
"""
 * @params string classNm (camel case style)
 *
 * @modeling >> 
 * class MyModelType(SQLAlchemyObjectType):
 *	class Meta:
 *		model = MyModel -> -> -> obj
 *		interfaces = (graphene.relay.Node,)
 *		exclude_fields = ("last_name",)
 *		only_fields = ("name",) 
 *	json_data = graphene.JSONString(source='json_data')
 *	data = graphene.Field(SubdataType, source='json_data')
 * 
 * @note 
"""
def dynamic_obj_type( obj=None, classNm='', dataSets={} ) :
	exclude_fields = ["is_active"]
	Xargs = {
		"Meta": type("Meta",(object,), {
			"model": obj
			,"interfaces" : (graphene.relay.Node,)
			,"exclude_fields" : exclude_fields
		}	)
	}

	if dataSets['columns'].get('json_data') and dataSets.get('json_querys') and dataSets.get('Obj'):
		Xargs['json_data'] = graphene.Field( dataSets['Obj'], source='json_data' )

	return type(
		classNm+'ObjType', (SQLAlchemyObjectType, ) 
		, Xargs
	)



## @brief Graphene List Entity ( classNmConnection )
"""
 * @params string classNm (camel case style)
 * 
 * @note 
"""
def dynamic_connection( obj=None, classNm='', dataSets={} ) :
	return type(
		classNm+'Connection', (graphene.ObjectType, ) 
		,{
			"pages" : graphene.Int()
			,"count" : graphene.Int()
			,"current" : graphene.Int()
			,"result" : graphene.List(obj)
		}
	)



## @breif Consumer Info 
"""
 * @memo get headers 
 * @param headers
 * @return JSON idx, secret
"""
def get_consumer_info (
	consumer = None
):
	if consumer is None:
		return False

	# print(consumer)
	xc.generate(consumer.get('bk-consumer-secret'))
	idx = xc.serviceNum( consumer.get('bk-consumer-id') )
	return {"idx" : idx, "secret" : consumer.get('bk-consumer-secret')  }



## @brief Create & Update ( Mutation Query )
"""
 * @see resolver > dynamic_mutation 
 * @todo 
"""
def get_mutate_qry (modelObj=None, headers=None, dataSets={}, **kwargs) :
	# get consumer 
	if dataSets.get('foreignKeys') is not None and 'Partners' in dataSets['foreignKeys']:
		consumer = get_consumer_info(headers)
		kwargs['partners_idx'] = consumer["idx"]
	
	# @note get Users information from AccessToken 
	if dataSets.get('foreignKeys') is not None and 'Users' in dataSets['foreignKeys']:
		if headers.get('Authorization') is None:
			return "ERROR : invalid token"
		
		getUsers = get_hash(
			headers.get('Authorization')
		, secret_key = SECRET_KEY
		, algorithm = ALGORITHM
		)
		if getUsers is False or isinstance(getUsers, dict) is False:
			return "ERROR : invalid token"
		kwargs['users_idx'] = int(getUsers['idx'])

	# args validation
	if kwargs.get( 'idx' ) is not None:
		# kwargs['idx'] = int(kwargs.get( 'idx' ))
		kwargs['idx'] = xc.feedNum(kwargs.get( 'idx' ))
	else:
		kwargs['idx'] = None

	if kwargs.get( 'is_active' ) is None:
		kwargs['is_active'] = 1
	
	if kwargs['idx'] is None :
		kwargs['create_date'] = int(time())
		kwargs['update_date'] = 0

	if dataSets['columns'].get('json_data') and dataSets.get('json_querys') :
		kwargs['json_data']=json.dumps(kwargs['json_data'], ensure_ascii=False)

	with Session() as session:
		newData = modelObj( **kwargs )
		# @note update newData
		if type(kwargs['idx']) is int and kwargs['idx']>0:
			newData = session.query( modelObj ).filter_by(idx=kwargs['idx']).first()

			# @note Post owner check
			if hasattr(newData, 'users_idx') : 
				if newData.users_idx != kwargs['users_idx']:
					return "ERROR : Not owner of this post"

			# @note Get class items key 
			for attr, value in newData.__dict__.items():
				# @note diff kwargs , object newData
				if kwargs.get(attr) is not None and getattr(newData, attr) != kwargs[attr]:
					# if attr != 'create_date':
					setattr(newData, attr, kwargs[attr])
			# @note Update current update date
			newData.update_date = int(time())

		session.add(newData)
		session.commit()
		session.refresh(newData)
		if dataSets['columns'].get('json_data') and dataSets.get('json_querys') :
			newData.json_data=json.loads( newData.json_data )
		# @note primary key hash
		newData.idx = xc.feedKey(newData.idx)
		# print(newData)
	return newData
	# return _function



## @brief get Access Token - - - - - -
"""
 * @see schema.Query 
"""
# get_hash ( jwt_token, secret_key = None, algorithm = 'HS256'):
def get_access_token (modelObj=None, headers=None, returnObj=None, userid='', passwd=''):
	consumer = get_consumer_info(headers)
	with Session() as session:
		result = session.query( modelObj ).filter_by(partners_idx=consumer["idx"], userid=userid).first()
		
		if result is not None and result.passwd == hash_password(passwd):
			access_token = create_access_token(
				data = {"idx": result.idx,  "lv" : result.level, "cid" : result.partners_idx  }
				, secret_key = SECRET_KEY
				, expires_delta = timedelta(minutes=EXPIRE_TIME)
				, algorithm = ALGORITHM
			)
			# Update 쿼리로 num 값을 증가시킴
			result.counter = result.counter + 1
			result.update_date = int(time())
			session.add(result)
			session.commit()

			msg="Success get Accesstoken"
		else:
			access_token = False
			msg="Don't Exist user information"
		return returnObj(token=access_token, msg=msg)


## @brief filter process
"""
 * @see schema.Query >> dynamic_resolver
"""
def get_where (modelObj, dataCols, wheres  ):
	pattern = re.compile(r'\b[a-zA-Z0-9]+\s*(?:>=|>|==|!=|<|<=)\s*\w+\b')
	pattern2 = re.compile(r'\b\s*(?:>|>=|==|!=|<=|<)\s*\b')
	dataCols['idx'] = 'idx'
	dataCols['update_date'] = 'date'
	dataCols['create_date'] = 'date'
	res = []
	for where in wheres:
		tmp = pattern.findall(where)
		tmp2 = pattern2.findall(where)
		if len(tmp)>0 and len(tmp2)>0:
			strings = tmp[0].split(tmp2[0])
			strings[0] = camelToSnake(strings[0].strip())
			strings[1] = strings[1].strip()
			if dataCols.get(strings[0]):
				if strings[0] == 'idx':
					strings[1] = int( xc.feedNum (strings[1]) )
				tmp2 = tmp2[0].strip()
				if strings[1].isdigit():
					strings[1] = int(strings[1])
				if tmp2 == '>':
					res.append( getattr( modelObj , strings[0]) > strings[1]  )
				if tmp2 == '>=':
					res.append( getattr( modelObj , strings[0]) >= strings[1]  )
				if tmp2 == '==':
					res.append( getattr( modelObj , strings[0]) == strings[1]  )
				if tmp2 == '!=':
					res.append( getattr( modelObj , strings[0]) != strings[1]  )
				if tmp2 == '<=':
					res.append( getattr( modelObj , strings[0]) <= strings[1]  )
				if tmp2 == '<':
					res.append( getattr( modelObj , strings[0]) < strings[1]  )
	return res



## @brief Read List Query
"""
 * @see schema.Query
"""
def dynamic_resolver (modelObj=None, listObj=None, classNm='', dataSets={}) :
	def _function (self, info, page=1, rows=15, search=None, sort='idx', asc=False, all=False, idx=None, where=[]):
		offset = (page-1)*rows
		pages = 1
		current = 1
		count = 1
		with Session() as session:
			res = session.query( modelObj )
			if idx is None :
				args = []
				args = get_where (modelObj, dataSets['columns'], where  )
				if len(args)>0:
					res = res.filter( and_( *args ) )
				# @note Apply Search word From text, varchar field
				if search:
					arg = []
					for colNm, colData in dataSets['columns'].items():
						if colData['type'] in type_str_ :
							arg.append( getattr( modelObj , colNm).ilike(f'%{search}%') )
					res = res.filter( or_( *arg ) )
				# @note Apply sorting
				if asc:
					res = res.order_by(getattr(modelObj, sort))
				else:
					res = res.order_by(getattr(modelObj, sort).desc())
				# @note Apply pagination
				count = res.count()
				# @note get all posts
				if all == False:
					pages = math.ceil(count/rows)
					if page > pages:
						current = pages
						offset = (current-1)*rows
					else:
						current = page
					if pages==0 :
						current = 0
						offset = 0

					res = res.offset(offset).limit(rows)
			else:
				idx = int( xc.feedNum (idx) )
				res = res.filter_by(idx=idx)

			# print(str(res))
			res = res.all()

			for key, value in enumerate(res):
				if dataSets['columns'].get('json_data') and dataSets.get('json_querys') :
					res[key].json_data = json.loads(res[key].json_data)
				res[key].idx = xc.feedKey(res[key].idx)

			return listObj (
				pages = pages,
				count = count,
				current = current,
				result = res
			)
	return _function






def partners_zero (partnersObj, usersObj) :
	newData = partnersObj (
		idx = 1
		,is_active = 1
		,create_date = int(time())
		,update_date = 0
		,users_idx = 1
		,site_id = 'www'
		,domain = 'bkfridays.com'
	)
	newData2 = usersObj (
		partners_idx = 1
		,idx = 1
		,is_active = 1
		,create_date = int(time())
		,update_date = 0
		,userid = MASTERID
		,user_name = MASTERNAME
		,passwd = hash_password(MASTERPW)
		,level = 99
		,counter = 0
	)
	with Session() as session:
		result= session.query(partnersObj).filter_by(idx = 1).first() 
		if result == None:
			session.add(newData)
			session.add(newData2)
			session.commit()
	return newData


