# standard library imports
import hashlib
import re
import urllib
# third party imports
import requests
# local imports
import config

class RSpaceObject:
	"""defines an object (resource) in resourcespace"""
	def __init__(self,
		rsid=None,
		csid=None,
		metadata=None,
		local_filepath=None,
		alternative_files=[(None,None)],
		derivative_url=None):
		self.rsid = rsid
		# the corresponding uuid in cspace for the object record related to this resource
		self.csid = csid
		self.metadata = metadata
		self.local_filepath = local_filepath
		# a list of tuples (rsid,local_filepath) for alt files
		self.alternative_files = alternative_files
		self.derivative_url = derivative_url


class RSpaceRequest:
	"""builds a request to rs"""
	def __init__(self,
		rs_api_function=None,
		parameters=None):

		self.rs_api_function = rs_api_function
		self.parameters = parameters
		self.rs_user = config.RS_USER
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

		# print(response)

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
		try:
			response = response.json()
		except:
			pass

		return response

def make_rsid_query_list(rsids=[],single_rsid=None):
	rsid_list = []
	if not rsids == []:
		for rsid in rsids:
			rsid_list.append(rsid['ref'])
		query_list = f"!list{':'.join([x for x in rsid_list])}"
	elif single_rsid:
		query_list = f"!list{single_rsid}"
		rsids = [{'ref':single_rsid}]
	return query_list,rsids

def filter_field_data_list(field_list,field_to_find):
	# print([x['value'] for x in field_list if x['name'] == field_to_find])
	try:
		value = "".join([x['value'] for x in field_list if x['name'] == field_to_find])
	except:
		value = None

	return value

def fetch_derivative_urls(rs_requester,resource_type,rsids=[],sinigle_rsid=None):
	# rsids should be a list of dicts from rs_utils.do_search()
	# return a list of dicts, now including the url for the deriv
	preview_query_string,rsids = make_rsid_query_list(rsids=rsids,single_rsid=sinigle_rsid)
	# print(preview_query_string)
	previews = rs_requester.search_get_previews(
		search_string=preview_query_string,
		resource_type=resource_type
		)
	# print("previews")
	# print(previews)
	url_key = 'url_'+config.DERIVATIVE_SIZE
	for x in previews:
		if url_key in x:
			for item in rsids:
				if x['ref'] == item['ref']:
					item['derivative url'] = re.match(r'(.+\.jpg).*',x[url_key]).group(1)
	# print(rsids)
	return rsids
