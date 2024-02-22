import json
import graphene
from utility import logX, camelToSnake
from database import Base, engine, JSON_MODELS, BASE_MODELS, Session
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from model import dynamic_models, dynamic_json_models
import resolver 


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


## @brief Dynamic Mutation  - - - - - -
"""
 * @params str classNm ( camel style )
 * @params dict dataSets
 *
 * @see resolver.get_mutate_qry
 * @see resolver.getGrapheneScalarsArgs
"""
def dynamic_mutation(classNm='', dataSets={}) :
	# @note Dynamic Arguments
	dynamicArgs = resolver.getGrapheneScalarsArgs(dataSets["columns"])
	# @note text json type (like nosql
	if dataSets['columns'].get('json_data') and dataSets.get('json_querys') :
		dynamicArgs['json_data'] = globals()[classNm+'InObj']()
		# @option required=True 

	# @note Mutate function
	def x_mutate (self, info, dataSets=dataSets, **kwargs):
		newData = resolver.get_mutate_qry(
			globals()[ classNm+'Model']
			, info.context["request"].headers
			, dataSets
			,  **kwargs
		)
		return globals()[classNm+'Mutation'](newData) 

	return type (
		classNm+'Mutation'
		, (graphene.Mutation, )
		, {
			"Arguments" : type ("Arguments", (object,) , dynamicArgs )
			, classNm : graphene.Field(lambda: globals()[classNm+'ObjType'] )
			, "mutate" : x_mutate
		}
	)



"""
 * @brief MAIN Process ===================
 * 
"""
with open(JSON_MODELS, 'r') as fp:
	jsonData=fp.read()

models = json.loads(jsonData)
loger = {
	"model" : [] 
	,"schmema" : []
	, "querys" : []
	, "mutations" : []
}



## @brief graphql Model Create - - - - - -
"""
 * @note Model Create
"""
for nm,val in models.items() :
	globals()[ nm+'Model'] = dynamic_models( nm ,val )
	loger["model"].append (nm+'Model')



## @brief DB Table Generate Insert DATA - - - - - -
"""
 * @note 
"""
# Base.metadata.drop_all(bind=engine)
# Base.metadata.reflect(bind=engine)
Base.metadata.create_all(bind=engine)

if BASE_MODELS == True:
	from model import PartnersModel, UsersModel
	resolver.partners_zero(PartnersModel, UsersModel)



## @brief access token schema type - - - - - -
class AccessTokenType(graphene.ObjectType):
	token = graphene.String()
	msg = graphene.String()



## @brief graphql Create Schema - - - - - -
"""
 * @note extends schema
"""
for nm,val in models.items() :
	if globals().get( nm+'Model' ) is not None:
		if val['columns'].get('json_data') and val.get('json_querys') :
			globals()[nm+'Obj'] = dynamic_json_models ( nm, 'Obj', val['json_querys'] )
			globals()[nm+'InObj'] = dynamic_json_models ( nm, 'InObj', val['json_querys'] )
			val['Obj'] = globals()[nm+'Obj']
		
		globals()[nm+'ObjType'] = resolver.dynamic_obj_type(globals()[nm+'Model'] , nm,  val )

		globals()[nm+'Connection'] = resolver.dynamic_connection( globals()[nm+'ObjType'] , nm, val )

		globals()[nm+'Mutation'] = dynamic_mutation ( nm, val)
		loger["schmema"].append (nm+'ObjType')



## @brief Query Generator - - - - - -
"""
 * @note Graphql Query 
 *
 * @see resolver.dynamic_resolver 
 * @see resolver.get_access_token 
"""
class Query(graphene.ObjectType):
	# info.context.META.get('HTTP_WHATEVER')
	access_token = graphene.Field(AccessTokenType, userid=graphene.ID(), passwd=graphene.String() )
	def resolve_access_token (self, info, userid, passwd ):
		return resolver.get_access_token (
			UsersModel
			, info.context["request"].headers
			, AccessTokenType
			, userid=userid
			, passwd=passwd
			)

	for nm,val in models.items() :
		locals()[camelToSnake(nm)] = graphene.Field(
			globals()[nm+'Connection']
			, page=graphene.Int(default_value=1)
			, rows=graphene.Int(default_value=15)
			, search=graphene.String()
			, sort=graphene.String(default_value='idx')
			, asc=graphene.Boolean(default_value=False)
			, all=graphene.Boolean(default_value=False)
			, idx=graphene.String()
		)

		locals()['resolve_'+camelToSnake(nm)] = resolver.dynamic_resolver (globals()[nm+'Model'], globals()[nm+'Connection'], nm, val)
		
		loger["querys"].append(camelToSnake(nm))



## @brief Mutation Generator - - - - - -
"""
 * @see graphene.Schema
"""
class Mutation(graphene.ObjectType):
	# create_my_model = CreateMyModelMutation.Field()
	for nm,val in models.items() :
		locals()['up_'+camelToSnake(nm)] = globals()[nm+'Mutation'].Field()
		loger["mutations"].append(camelToSnake(nm))


# logX ("Create All", loger, "INFO")

schemaQry = graphene.Schema(query=Query, mutation=Mutation)

