# standard library imports
import hashlib
# third party imports
import requests
# local imports
import config



class RSpaceRequest:
	"""builds a request to rs"""
	def __init__(self,
		rs_api_function=None,
		parameters=None):

		self.rs_api_function = rs_api_function
		self.parameters = self.format_params(parameters)
		self.rs_user = config.RS_USER
		print(self.rs_user)
		self.rs_userkey = config.RS_USERKEY
		self.rs_url = config.RS_URL
		self.query_url = None

	def format_params(self,parameters):
		params = "&".join(["{}={}".format(k,v) for k,v in parameters.items()])
		return params

	def make_query(self):
		query = "user={}&function={}&{}".format(
			self.rs_user,
			self.rs_api_function,
			self.parameters
			)
		print(query)
		sign = hashlib.sha256(self.rs_userkey.encode()+query.encode())
		sign = sign.hexdigest()
		print(sign)
		self.query_url = "{}/?{}&sign={}".format(
			self.rs_url,
			query,
			sign
			)

	def post_query(self):
		if not self.query_url:
			sys.exit(1)
		response = requests.post(self.query_url)

		return response


def get_resource_data(rs_api_function, parameters):
	# or like this?
	# kwargs = parameters for api call
	pass

def do_search(search_string=None, resource_type=None):
	search = RSpaceRequest(
		rs_api_function="do_search",
		parameters = {
				"$search":search_string,
				"$restypes":resource_type
			}
		)

	search.make_query()
	response = search.post_query()

	print(response.text)
	return response
