import os, json, sys, re, hashlib
from time import time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from typing import Union


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

## @brief custom loging
"""
 * @note 
 * @see 
"""
def logX (t="", m="", lv="INFO"):
	print (
		json.dumps ({
			"level": lv
			,"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			,"path" : sys._getframe(1).f_code.co_name
			,"title": t
			,"message": m
		},ensure_ascii=False, indent=2 )
		+ ","
	)



## @brief case style convert
"""
 * @note 
 * @see 
"""
def camelToSnake(s):
	camel = re.compile(r'(.)([A-Z][a-z]+)')
	to_snake = re.compile('([a-z0-9])([A-Z])')
	return to_snake.sub(r'\1_\2', camel.sub(r'\1_\2', s)).lower()



## @breif PASSWORD
"""
 * @param password
"""
def hash_password(password):
	hash_object = hashlib.sha3_512(password.encode())
	hashed_password = hash_object.hexdigest()
	return hashed_password



## @breif Generate Access Token (JWT)
"""
 * @param data
 * @param secret_key
 * @param expires_delta
 * @param algorithm
"""
def create_access_token(
	data: dict
	, secret_key = None
	, expires_delta: Union[timedelta, None] = None
	, algorithm = 'HS256'
):
	if secret_key == None:
		return False
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
	return encoded_jwt



## @breif Get Token hash
"""
 * @param jwt_token
 * @param secret_key
 * @param algorithm
"""
def get_hash (
	jwt_token
	, secret_key = None
	, algorithm = 'HS256'
):
	if secret_key == None:
		return False
	if jwt_token.split(" ")[0] != 'Bearer':
		return False
	# Decode a JWT token
	decoded_token = jwt.decode(jwt_token.split(" ")[-1], secret_key, algorithms=[algorithm])
	return decoded_token



class Xcrypt():
	base = 0
	alphabet = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	MEMBER_DESC=10223372036854775807
	FEED_DESC=36893488147419103230
	SERVICE_DESC=4294967295
	key = None
	# @breif init 
	def __init__(self):
		self.base = len(self.alphabet)

	# @brief hash key generator
	def generate (self, key=None):
		if key is None: 
			key = Fernet.generate_key() # gen key
		self.key = key
		self.f   = Fernet(self.key)

	# @brief bijection encode
	def num2str(self, number):
		if number == 0:
			return self.alphabet[0]
		s = ''
		while number >= self.base:
			remainder = number % self.base
			number = int(number // self.base)
			s += self.alphabet[remainder]
		if number < self.base and number > 0 :
			s += self.alphabet[number]
		return s[::-1] # reverse string

	# @brief bijection decode
	def str2num(self, s):
		i = 0
		for char in s:
			i = i * self.base + self.alphabet.index(char)
		return i

	# @brief check byte
	def checkB (self, d):
		if isinstance(d, bytes):
			return d
		else:
			return d.encode('utf-8')

	# @brief 
	def outStr (self, data, is_out_string=True):
		if is_out_string is True:
			return data.decode('utf-8')
		else:
			return data

	# @brief encrypt
	def encrypt(self, data, is_out_string=True):
		return self.outStr (
			self.f.encrypt( self.checkB(data) )  
			, is_out_string
		)

	# @brief decrypt
	def decrypt(self, data, is_out_string=True):
		return self.outStr (
			self.f.decrypt( self.checkB(data) )  
			, is_out_string
		)

	# @brief Encrypt Service
	def serviceKey (self, serviceNum):
		return self.encrypt( self.num2str( (self.SERVICE_DESC - serviceNum) ) )

	# @brief User key Encode
	def userKey (self, serviceNum):
		return self.num2str( (self.MEMBER_DESC - serviceNum) ) 

	# @brief Feed key Encode
	def feedKey (self, serviceNum):
		return self.num2str( (self.FEED_DESC - serviceNum) ) 

	# @brief Decrypt Service
	def serviceNum (self, serviceStr):
		return self.SERVICE_DESC - self.str2num( self.decrypt( serviceStr ) )

	# @brief User num Decode
	def userNum (self, serviceStr):
		return self.MEMBER_DESC - self.str2num(  serviceStr ) 

	# @brief Feed num Decode
	def feedNum (self, serviceStr):
		return self.FEED_DESC - self.str2num(  serviceStr )


