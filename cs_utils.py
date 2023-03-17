# standard library imports
import base64
from pathlib import Path
import re
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
		self.cspace_object_base_url = self.instance_config['cspace_object_base_url']

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

	def make_url(self,csid):
		url = f"{self.cspace_object_base_url}/{csid}"

		return url

def parse_paged_response(response,cs_requester):
	# get the csid for hopefully the one item in a search by acc no
	csid = uri = None
	tree = etree.XML(response.encode())
	# print(tree)
	number_of_results = tree.findtext('totalItems')
	# print(number_of_results)
	if int(number_of_results) == 1:
		csid = tree.find(".//csid").text
		url = cs_requester.make_url(csid)
		# print(csid)
	return csid,url

def get_item_data(csid,cs_requester):
	print(csid)
	response = cs_requester.run_query(
		cspace_service='collectionobjects',
		parameters="/"+csid)
	full_item_xml = etree.XML(response.text.encode())
	# print(full_item_xml)
	fields_to_extract = cs_requester.instance_config['fields_to_extract']
	temp={}
	for k,v in fields_to_extract.items():
		print(v)
		try:
			temp[k] = ", ".join(full_item_xml.iterfind(f".//{v}"))
			print(temp[k])
		except:
			print(full_item_xml.find(f".//{v}"))
	print(temp)
	return temp

def fetch_cs_metadata(rs_item,rs_requester,cs_object_id,cs_requester):
	# fetch and update metadata from cspace to resourcespace
	# rs_item should be a RSpaceObject instance
	response = cs_requester.run_query(
		cspace_service='collectionobjects',
		parameters=f"?as=collectionobjects_common:objectNumber='{cs_object_id}'"
		)
	# print(response.text)
	try:
		csid,url = parse_paged_response(response.text,cs_requester)
		# print(url)
	except:
		csid = None
	if csid:
		# print("csid????")
		# print(csid)
		rs_item.csid = csid
		rs_item.metadata = get_item_data(csid,cs_requester)

		if rs_item.metadata:
			rs_requester.update_field(resource_id=rs_item.rsid,field_id="116",value=cs_requester.make_url(csid))
			for k,v in rs_item.metadata.items():
				if v:
					rs_requester.update_field(
						resource_id=rs_item.rsid,
						field_id=k,
						value=v)

	return rs_item

def push_derivative(rs_item,cs_requester,rs_requester):
	# rs_item should be a RSpaceObject instance
	return_value = False
	response = cs_requester.run_query(
		cspace_service='media',
		parameters=f'?blobUri={rs_item.derivative_url}',
		verb='post',
		payload = media_payload
	)
	if response.ok:
		media_uri = response.headers['Location']
		media_csid = re.match('.+\/([a-fA-F0-9-]+)',media_uri).group(1)
		payload = relation_payload.format(rs_item.csid,media_csid)
		rev_payload = reverse_payload.format(media_csid,rs_item.csid)
		# print(payload)
		response = cs_requester.run_query(
			cspace_service='relations',
			verb='post',
			payload=payload
		)
		response = cs_requester.run_query(
			cspace_service='relations',
			verb='post',
			payload=rev_payload
		)
		# print(response.headers['Location'])

		if response.ok:
			response = rs_requester.update_field(
				resource_id=rs_item.rsid,
				# here again the synced field ID should come from config
				field_id='111',
				value='true'
			)
			return_value = True

	return return_value

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
	  <subjectDocumentType>collectionobjects</subjectDocumentType>
	  <relationshipType>affects</relationshipType>
	  <objectCsid>{}</objectCsid>
	  <objectDocumentType>media</objectDocumentType>
	</ns2:relations_common>
</document>
"""

reverse_payload="""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
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
