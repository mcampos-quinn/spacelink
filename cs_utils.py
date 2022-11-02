import base64
from pathlib import Path
import urllib
from urllib.parse import urljoin

from lxml import etree
import requests

import config

class CSpaceRequest:
	"""builds a request to cspace"""
	def __init__(self,
		csid=None,
		cspace_instance=None):
		self.csid = csid
		self.cspace_instance = cspace_instance
		self.instance_config = config.CSPACE_INSTANCE[cspace_instance]
		self.cspace_services_url = self.instance_config['cspace_services_url']
		# self.auth = base64.b64encode("{}:{}".format(
		# 	config.CSPACE_INSTANCE[cspace_instance]['CSPACE_USER'],
		# 	config.CSPACE_INSTANCE[cspace_instance]['CSPACE_PASSWORD']
		# 	).encode()
		# )

	def run_query(self,cspace_service=None,parameters=None,verb="get",headers=None):
		url = f"{self.cspace_services_url}/{cspace_service}{parameters}"
		print(url)
		if verb == "get":
			response = requests.get(url,auth=(
				config.CSPACE_USER,
				config.CSPACE_PASSWORD
				)
			)
		elif verb == 'post':
			headers = {"Content-Type":"application/xml"}
			response = requests.post(url,auth=(
				config.CSPACE_USER,
				config.CSPACE_PASSWORD
				),
				headers=headers
			)
			print(response.text)
		return response.text

	def parse_paged_response(self,response):
		# get the csid for hopefully the one item in a search by acc no
		csid = uri = None
		# print(response)
		tree = etree.XML(response.encode())
		# print(tree)
		number_of_results = tree.findtext('totalItems')
		# print(number_of_results)
		if int(number_of_results) == 1:
			csid = tree.find(".//csid").text
			uri = tree.find(".//uri").text
			# print(csid)
		return csid,uri

	def get_item_data(self,csid):
		response = self.run_query(
			cspace_service='collectionobjects',
			parameters="/"+csid)
		full_item_xml = etree.XML(response.encode())
		# print(full_item_xml)
		fields_to_extract = self.instance_config['fields_to_extract']
		temp={}
		for k,v in fields_to_extract.items():
			# print(v)
			temp[k] = full_item_xml.find(f".//{v}").text
		# print(temp)
		return temp
