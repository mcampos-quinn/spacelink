"""
This will be the initial nightly sync between cspace and resourcespace for
the art collection.
1) query rs for new items, using a 'synced' field (true/false, default of null)
2) get an accession number from the filename or from an auto-populated accession
	number field, TBD
3) Query cspace using the accession number, returning metadata for the object
4) Add the metadata to the RS item, and also send a specified derivative size to
	CS, creating media & blob records, then a relation record to the original
	object
5) If all is kosher, update the RS item with synced=true
"""
# standard library imports
from datetime import datetime
from pathlib import Path
import re
import sys
import urllib

# local imports
import config
import cs_utils
import rs_utils

# usage
# `python3 nightlink.py MY_CSPACE_INSTANCE`
cspace_instance = sys.argv[1]
if cspace_instance in config.CSPACE_INSTANCE:
	cspace_services_url = config.CSPACE_INSTANCE[cspace_instance]['cspace_services_url']
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	print("ok")
else:
	sys.exit(1)

cspace_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
rs_requester = rs_utils.RSpaceRequest()

# return a list of resource ids for new items (field 101, 'synced' is empty)
# this should also be set in config rather than hard coded
rsids = rs_requester.do_search(
	search_string="!empty101",
	resource_type=resource_type
	)
# now go back and get the url for the relevant preview size (set in config)
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

for resource in rsids:
	item = rs_utils.RSpaceObject(rsid=resource['ref'])
	print(resource['field8'])
	# object_number will be from a parsed filename, or from an accession number field directly
	object_number = "2021.16.1"
	# on second thought the below request could just be a simple call to
	# url/cspace-services/collectionobjects/{object_number}
	response = cspace_requester.run_query(
		cspace_service='collectionobjects',
		parameters=f"?as=collectionobjects_common:objectNumber='{object_number}'"
		)
	csid,uri = cspace_requester.parse_paged_response(response.text)
	if csid:
		item.metadata = cspace_requester.get_item_data(csid)
		for k,v in item.metadata.items():
			if v:

				rs_requester.update_field(
					resource_id=item.rsid,
					field_id=k,
					value=v)
		response = cspace_requester.run_query(
			cspace_service='media',
			parameters=f'?blobUri={resource[url_key]}',
			verb='post',
			payload = cs_utils.media_payload
		)
		if response.ok:
			media_uri = response.headers['Location']
			media_csid = re.match('.+\/([a-fA-F0-9-]+)',media_uri).group(1)
			payload = cs_utils.relation_payload.format(media_csid,csid)
			response = cspace_requester.run_query(
				cspace_service='relations',
				verb='post',
				payload=payload
			)
			if response.ok:
				response = rs_requester.update_field(
					resource_id=item.rsid,
					# here again the synced field ID should come from config
					field_id='101',
					value='true'
				)
