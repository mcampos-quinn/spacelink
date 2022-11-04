# standard library imports
import hashlib
import urllib
# third party imports
import requests
# local imports
import config

class RSpaceObject:
	"""defines an object (resource) in resourcespace"""
	def __init__(self,
		rsid=None,
		metadata={},
		local_filepath=None,
		alternative_files=[(None,None)]):
		self.rsid = rsid
		self.metadata = metadata
		self.local_filepath = local_filepath
		# a list of tuples (rsid,local_filepath) for alt files
		self.alternative_files = alternative_files


class RSpaceRequest:
	"""builds a request to rs"""
	def __init__(self,
		rs_api_function=None,
		parameters=None):

		self.rs_api_function = rs_api_function
		self.parameters = parameters
		self.rs_user = config.RS_USER
		# print(self.rs_user)
		self.rs_userkey = config.RS_USERKEY
		self.rs_url = config.RS_URL
		self.query_url = None

	def format_params(self,parameters):
		params = "&".join(["{}={}".format(k,v) for k,v in parameters.items()])
		return params

	def search_get_previews(self,search_string=None,resource_type=None):
		self.rs_api_function = "search_get_previews"
		self.parameters = self.format_params({
			"search":search_string,
			"restypes":resource_type,
			"getsizes":config.DERIVATIVE_SIZE
			})
		self.make_query()
		response = self.post_query()

		return response

	def do_search(self, search_string=None, resource_type=None):
		self.rs_api_function = "do_search"
		self.parameters = self.format_params({
			"search":search_string,
			"restypes":resource_type,
			"getsizes":config.DERIVATIVE_SIZE
			})
		self.make_query()
		response = self.post_query()

		# print(response.text)
		return response

	def update_field(self,resource_id=None,field_id=None,value=None):
		self.rs_api_function = "update_field"
		self.parameters = self.format_params({
			"resource":resource_id,
			"field":field_id,
			"value":urllib.parse.quote_plus(value)
		})
		self.make_query()
		response = self.post_query()
		# print(response)
		return response

	def make_query(self):
		query = "user={}&function={}&{}".format(
			self.rs_user,
			self.rs_api_function,
			self.parameters
			)
		# print(query)
		sign = hashlib.sha256(self.rs_userkey.encode()+query.encode())
		sign = sign.hexdigest()
		# print(sign)
		self.query_url = "{}/?{}&sign={}".format(
			self.rs_url,
			query,
			sign
			)
		# print(self.query_url)

	def post_query(self):
		if not self.query_url:
			sys.exit(1) # lol this needs to be less extreme
		response = requests.post(self.query_url)
		try:
			response = response.json()
		except:
			pass

		return response

def make_rsid_query_list(rsids=[]):
	rsid_list = []
	if not rsids == []:
		for rsid in rsids:
			rsid_list.append(rsid['ref'])
	query_list = f"!list{':'.join([x for x in rsid_list])}"
	return query_list

def get_resource_data(rs_api_function, parameters):
	# or like this?
	# kwargs = parameters for api call
	pass
