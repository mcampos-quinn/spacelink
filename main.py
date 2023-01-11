from fastapi import FastAPI
# local imports
import config
import cs_utils
import link_log
import rs_utils

'''
run local dev server:
$ uvicorn main:app --reload
'''

app = FastAPI()

@app.post("/validate_cs_object_id/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, validate the cspace object ID entered within resourcespace metadata
# Note: this adds/updates the metadata from CSpace
async def validate_cs_object_id(cspace_instance,resource_id):
	current_link_log = link_log.LinkLog()
	return_value = {"Valid":False,"CSID":""}
	rs_requester = rs_utils.RSpaceRequest()
	resource_obj=rs_utils.RSpaceObject(rsid=resource_id)
	cs_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)

	resource_dict_list = [{"ref":resource_id}]
	resource_obj_list = rs_utils.make_resource_objs(resource_dict_list)
	resource_obj = rs_utils.validate_cs_object_id(resource_obj_list[0],rs_requester,cs_requester)
	if resource_obj.csid:
		current_link_log.logger.info(f"CSpace object ID is valid for RSpace item {resource_obj.rsid}")
		current_link_log.logger.info(f"Successfully synced RSpace item {resource_obj.rsid}")
		return_value = {"Valid":True,"CSID":resource_obj.csid}
	else:
		current_link_log.logger.warning(f"Invalid/incorrect CSpace object ID for RSpace item {resource_obj.rsid}!!")
		rs_requester.update_field(rsid=resource_obj.rsid,field="118",value="Invalid/incorrect cspace object ID!")
		return_value = {"Valid":"Invalid CSpace Object ID!","CSID":None}

	return return_value

@app.post("/push_image/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, get the cspace object ID, and push the derivative to the CSpace record
# Note: this adds/updates the metadata from CSpace
async def push_image(cspace_instance,resource_id):
	current_link_log = link_log.LinkLog()
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	pushed = False
	return_value = {"Outcome":False}

	resource_obj = rs_utils.RSpaceObject(rsid=resource_id)
	rs_requester = rs_utils.RSpaceRequest()
	cs_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	field_data = rs_requester.get_resource_field_data(resource_id=resource_id)
	if field_data:
		resource_obj_list = rs_utils.fetch_derivative_urls(
			rs_requester,
			resource_type,
			resource_obj_list=[resource_obj]
			)
		item = rsids[0]
		# resource_obj.derivative_url = item['derivative url']
		# this should be set in config
		cs_object_id = rs_utils.filter_field_data_list(field_data,'accessionnumber')
		if cs_object_id:
			# if it has a csid, use it
			resource_obj = cs_utils.fetch_cs_metadata(
				resource_obj,
				rs_requester,
				cs_object_id,
				cs_requester
				)
			pushed = cs_utils.push_derivative(resource_obj,cs_requester,rs_requester)
			if pushed:
				current_link_log.logger.info(f"Successfully synced RSpace item {resource_obj.rsid}")
				return_value = {"Outcome":True}
			else:
				current_link_log.logger.warning(f"Unable to push image for RSpace item {resource_obj.rsid}!!")
				return_value = {"Outcome":f"Unable to push the derivative for resource {resource_obj.rsid}!"}
		else:
			current_link_log.logger.warning(f"RSpace item {resource_obj.rsid} doesnt have a CSpace object ID??")

	return return_value

@app.post("/push_image_group/{cspace_instance}/{resource_id}")
# using the resource id, query for the value (set in config.py?) in the RS record that will be used
# to define a "group" within RS. For example, reource 31 will have a "cinefiles_id"
# value of 60113, which is re-queried to form a "group" that will all have their
# derivatives pushed to the relevant cspace record
async def push_image_group(cspace_instance,resource_id):
	pass
