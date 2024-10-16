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
import logging
from pathlib import Path
import re
import sys
import urllib

# local imports
import config
import cs_utils
import link_log
import rs_utils

current_link_log = link_log.LinkLog()
# usage
# `python3 nightlink.py MY_CSPACE_INSTANCE`
cspace_instance = sys.argv[1]
if cspace_instance in config.CSPACE_INSTANCE:
	cspace_services_url = config.CSPACE_INSTANCE[cspace_instance]['cspace_services_url']
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	print("ok")
else:
	current_link_log.logger.warning("config is misconfigured, fix it!!")
	sys.exit(1)

cs_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
rs_requester = rs_utils.RSpaceRequest()
rs_requester.check_status()

if not rs_requester.status:
	current_link_log.logger.warning("The ResourceSpace API is broken or misconfigured.")
	sys.exit(1)

# return a list of resource ids for new items (e.g. where resourcespace field 101, 'synced,' is empty)
sync_check_field = config.CSPACE_INSTANCE[cspace_instance]['rspace_sync_check_field']
resource_dict_list = rs_requester.do_search(
	search_string = f"!empty{sync_check_field}",
	resource_type = resource_type
	)
if resource_dict_list == []:
	# nothing to do, quit and log
	current_link_log.logger.info("No new images today :(")
	sys.exit(0)
# print(resource_dict_list)
resource_obj_list = rs_utils.make_resource_objs(resource_dict_list)

temp = []
for resource_obj in resource_obj_list:
	resource_obj = rs_utils.validate_cs_object_id(resource_obj,rs_requester,cs_requester)
	if not resource_obj.csid:
		# log the error and/or add the note to the record in rspace
		current_link_log.logger.warning(f"Invalid/incorrect CSpace object ID for RSpace item {resource_obj.rsid}!!")
		# this should be set in config
		rs_requester.update_field(resource_id=resource_obj.rsid,field_id="118",value="Invalid/incorrect cspace object ID!")
		rs_requester.update_field(resource_id=resource_obj.rsid,field_id=sync_check_field,value="False")
	else:
		temp.append(resource_obj)
resource_obj_list = temp

resource_obj_list = rs_utils.fetch_derivative_urls(
	rs_requester,
	resource_type,
	resource_obj_list=resource_obj_list
	)
for resource_obj in resource_obj_list:
	pushed = cs_utils.push_derivative(resource_obj,cs_requester,rs_requester)
	if pushed:
		current_link_log.logger.info(f"Successfully synced RS item {resource_obj.rsid}")
