# standard library imports
import base64
from pathlib import Path
import urllib
from urllib.parse import urljoin
# third party imports
from lxml import etree
import requests
# local imports
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

	def run_query(self,cspace_service=None,parameters="",verb="get",headers=None,payload=None):
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
				headers=headers,
				data=payload
			)
			# print(response.text)
		return response

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
			url = self.make_url(uri)
			# print(csid)
		return csid,url

	def make_url(self,uri):
		url = f"{self.cspace_services_url.replace('/cspace-services','')}{uri}"

		return url

	def get_item_data(self,csid):
		response = self.run_query(
			cspace_service='collectionobjects',
			parameters="/"+csid)
		full_item_xml = etree.XML(response.text.encode())
		# print(full_item_xml)
		fields_to_extract = self.instance_config['fields_to_extract']
		temp={}
		for k,v in fields_to_extract.items():
			# print(v)
			temp[k] = full_item_xml.find(f".//{v}").text
		# print(temp)
		return temp

media_payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="media">
<ns2:media_common xmlns:ns2="http://collectionspace.org/services/media" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</ns2:media_common>
</document>
"""

relation_payload="""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<document>
	<ns2:relations_common xmlns:ns2="http://collectionspace.org/services/relation">
	  <subjectCsid>{}</subjectCsid>
	  <subjectDocumentType>media</subjectDocumentType>
	  <relationshipType>affects</relationshipType>
	  <objectCsid>{}</objectCsid>
	  <objectDocumentType>collectionobjects</objectDocumentType>
	</ns2:relations_common>
</document>
"""
