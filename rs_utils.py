# standard library imports
import hashlib
import re
import urllib
# third party imports
import requests
# local imports
import config
import cs_utils

class RSpaceObject:
	"""defines an object (resource) in resourcespace"""
	def __init__(self,
		rsid=None,
		csid=None,
		metadata=None,
		local_filepath=None,
		filename=None,
		alternative_files=[(None,None)],
		derivative_url=None):
		self.rsid = rsid
		# the corresponding uuid in cspace for the object record related to this resource
		self.csid = csid
		self.metadata = metadata
		self.local_filepath = local_filepath
		self.filename = filename
		# a list of tuples (rsid,local_filepath) for alt files
		self.alternative_files = alternative_files
		self.derivative_url = derivative_url


class RSpaceRequest:
	"""builds a request to rs"""
	def __init__(self,
		rs_api_function=None,
		parameters=None):

		self.status = None
		self.rs_api_function = rs_api_function
		self.parameters = parameters
		self.rs_user = config.RS_USER
		self.rs_userkey = config.RS_USERKEY
		self.rs_url = config.RS_URL
		self.query_url = None

		# self.check_status()

	def check_status(self):
		self.rs_api_function = "get_system_status"
		self.make_query()
		response = self.post_query()
		if not response:
			self.status = None
		else:
			self.status = True

	def format_params(self,parameters):
		params = "&".join(["{}={}".format(k,v) for k,v in parameters.items()])
		return params

	def search_get_previews(self,search_string=None,resource_type=None,size=",".join(config.DERIVATIVE_SIZES)):
		self.rs_api_function = "search_get_previews"
		self.parameters = self.format_params({
			"search":search_string,
			"restypes":resource_type,
			"getsizes":size
			})
		self.make_query()
		response = self.post_query()

		# print(response)

		return response

	def do_search(self, search_string=None, resource_type=None,size=None):
		self.rs_api_function = "do_search"
		self.parameters = self.format_params({
			"search":search_string,
			"restypes":resource_type,
			"getsizes":size
			})
		self.make_query()
		response = self.post_query()

		return response

	def get_resource_field_data(self,resource_id=None):
		self.rs_api_function = "get_resource_field_data"
		self.parameters = self.format_params({"resource":f"{resource_id}"})
		self.make_query()
		response = self.post_query()

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

		return response

	def make_query(self):
		query = "user={}&function={}&{}".format(
			self.rs_user,
			self.rs_api_function,
			self.parameters
			)
		sign = hashlib.sha256(self.rs_userkey.encode()+query.encode())
		sign = sign.hexdigest()
		self.query_url = "{}/?{}&sign={}".format(
			self.rs_url,
			query,
			sign
			)
		print(self.query_url)

	def post_query(self):
		if not self.query_url:
			sys.exit(1) # lol this needs to be less extreme
		response = requests.post(self.query_url)
		if str(response.status_code).startswith('20'):
			try:
				response = response.json()
			except:
				pass
		else:
			response = None

		return response

def make_resource_objs(resource_dict_list):
	resource_obj_list = []
	for item in resource_dict_list:
		rsid = item['ref']
		resource = RSpaceObject(rsid=rsid)
		resource_obj_list.append(resource)

	return resource_obj_list

def make_rsid_query_list(resource_obj_list=[]):#,single_resource=None):
	# take in a list of RSpaceObject instances and make a query string for RS
	rsid_list = []
	if len(resource_obj_list) > 1:
		for resource in resource_obj_list:
			rsid_list.append(resource.rsid)
		query_list = f"!list{':'.join([str(x) for x in rsid_list])}"
	elif len(resource_obj_list) == 1:
		query_list = f"!list{str(resource_obj_list[0].rsid)}"
		# rsids = [{'ref':single_rsid}]
	else:
		query_list = None
	return query_list#,rsids

def filter_field_data_list(field_list,field_to_find):
	# print([x['value'] for x in field_list if x['name'] == field_to_find])
	try:
		value = "".join([x['value'] for x in field_list if x['name'] == field_to_find])
	except:
		value = None

	return value

def validate_cs_object_id(resource_obj,rs_requester,cs_requester):
	field_data = rs_requester.get_resource_field_data(resource_id=resource_obj.rsid)
	# print(field_data)
	resource_obj.filename = filter_field_data_list(field_data,'originalfilename')
	cs_object_id = filter_field_data_list(field_data,'accessionnumber')
	if cs_object_id:
		resource_obj = cs_utils.fetch_cs_metadata(
			resource_obj,
			rs_requester,
			cs_object_id,
			cs_requester
			)

	return resource_obj

def fetch_derivative_urls(rs_requester,resource_type,resource_obj_list=[]):#,single_resource=None):
	# resource_obj_list should be a list of RSpaceObject instances
	# return the list, now including the url for the deriv
	preview_query_string = make_rsid_query_list(resource_obj_list=resource_obj_list)#,single_resource=single_resource)
	previews = rs_requester.search_get_previews(
		search_string=preview_query_string,
		resource_type=resource_type
		)
	for item in resource_obj_list:
		for size in config.DERIVATIVE_SIZES:
			url_key = 'url_'+size
			for x in previews:
				if url_key in x:
					if str(x['ref']) == str(item.rsid):
						item.derivative_url = re.match(r'(.+\.jpg).*',x[url_key]).group(1)
			if item.derivative_url:
				print("ITEM DERIV URL"+str(item.derivative_url))
				break

	return resource_obj_list
