"""
This will be the initial nightly sync between cspace and resourcespace

1) query rs for new images [SHOULD THIS BE BY DATETIME OR BY 'SYNCED' FIELD?]
2) using list of returned rsids query again for:
	- filename,

"""
from datetime import datetime
from pathlib import Path
import sys

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

counter = 0
for resource in rsids:
	counter += 1
	item = rs_utils.RSpaceObject(rsid=resource['ref'])
	if counter < 5:
		# print(resource)
		# print(type(resource))
		print(resource['field8'])
		# object_number will be from a parsed filename, or from an accession number field directly
		object_number = "2021.16.1"
		response = cspace_requester.run_query(
			cspace_service='collectionobjects',
			parameters="?as=collectionobjects_common:objectNumber='{}'".format(
				object_number
				)
			)
		# print(response)
		csid,uri = cspace_requester.parse_paged_response(response)
		# print(csid)
		if csid:
			item.metadata = cspace_requester.get_item_data(csid)
			for k,v in item.metadata.items():
				if v:
					rs_requester.update_field(
						resource_id=item.rsid,
						field_id=k,
						value=v)


	# search cspace based on parsed filename

	# put required fields into dict/json

	# post that back to rs

# print(len(list(rsids)))
