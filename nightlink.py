"""
This will be the initial nightly sync between cspace and resourcespace

1) query rs for new images [SHOULD THIS BE BY DATETIME OR BY 'SYNCED' FIELD?]
2) using list of returned rsids query again for:
	- filename,

"""
from datetime import datetime
from pathlib import Path
import re
import sys
import urllib

import config
import cs_utils
import rs_utils

cspace_instance = sys.argv[1]
if cspace_instance in config.CSPACE_INSTANCE:
	cspace_services_url = config.CSPACE_INSTANCE[cspace_instance]['cspace_services_url']
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	print("ok")
else:
	sys.exit(1)

cspace_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
rs_requester = rs_utils.RSpaceRequest()

# return a list of resource ids for new items
rsids = rs_requester.do_search(
	search_string="!empty101",
	resource_type=resource_type
	)
# now go back and add the url for the relevant preview size (set in config)
preview_query_string = rs_utils.make_rsid_query_list(rsids)
previews = rs_requester.search_get_previews(
	search_string=preview_query_string,
	resource_type=resource_type
	)

url_key = 'url_'+config.DERIVATIVE_SIZE
for x in previews:
	if url_key in x:
		for y in rsids:
			if x['ref'] == y['ref']:
				y[url_key] = re.match(r'(.+\.jpg).*',x[url_key]).group(1)

counter = 0
for resource in rsids:
	counter += 1
	# print(resource)
	item = rs_utils.RSpaceObject(rsid=resource['ref'])
	if counter < 5:
		print(resource['field8'])
		# object_number will be from a parsed filename, or from an accession number field directly
		object_number = "2021.16.1"
		response = cspace_requester.run_query(
			cspace_service='collectionobjects',
			parameters=f"?as=collectionobjects_common:objectNumber='{object_number}'"
			)
		# print(response)
		csid,uri = cspace_requester.parse_paged_response(response.text)
		# print(csid)
		if csid:
			item.metadata = cspace_requester.get_item_data(csid)
			for k,v in item.metadata.items():
				if v:
					rs_requester.update_field(
						resource_id=item.rsid,
						field_id=k,
						value=v)
					# blob_url = urllib.parse.quote_plus(f'{}')
					response = cspace_requester.run_query(
						cspace_service='media',
						parameters=f'?blobUri={resource[url_key]}',
						verb='post',
						payload = cs_utils.media_payload
					)
					# print(response.ok)
					if response.ok:
						media_uri = response.headers['Location']
						# print(media_uri)
						media_csid = re.match('.+\/([a-fA-F0-9-]+)',media_uri).group(1)
						# print(media_csid)
						payload = cs_utils.relation_payload.format(media_csid,csid)
						# print(payload)
						response = cspace_requester.run_query(
							cspace_service='relations',
							verb='post',
							payload=payload
						)
						# print(response.status_code)
						# print(response.text)
						if response.ok:
							response = rs_requester.update_field(
								resource_id=item.rsid,
								field_id='101',
								value='true'
							)
							print(response)
