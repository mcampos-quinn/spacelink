"""
This will be the nightly sync between cspace and resourcespace

1) query rs for new images [SHOULD THIS BE BY DATETIME OR BY 'SYNCED' FIELD?]
2) using list of returned rsids query again for:
	- filename,

"""
from datetime import datetime
from pathlib import Path
import sys

import config
import rs_utils

cspace_instance = sys.argv[1]
if cspace_instance in config.CSPACE_INSTANCE:
	base_url = config.CSPACE_INSTANCE[cspace_instance]['url']
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	print("ok")
else:
	sys.exit(1)

# return a list of resource ids for new items
rsids = rs_utils.do_search(
	search_string="!empty101",
	resource_type=resource_type
	)

rsids = rsids
# print(type(rsids))
# print(len(rsids))

for resource in rsids:
	# print(resource)
	# print(type(resource))
	print(resource['field8'])

# print(len(list(rsids)))
