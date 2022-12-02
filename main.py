from fastapi import FastAPI
# local imports
import config
import cs_utils
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
	return_value = {"Valid":False,"URL":""}
	rs_requester = rs_utils.RSpaceRequest()
	rs_item=rs_utils.RSpaceObject(rsid=resource_id)
	cs_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	response = rs_requester.get_resource_field_data(resource_id=resource_id)
	if response:
		# i suppose 'accessionnumber' could also be set in config since it's
		# defined within the rs instance rather than hard-coded
		# cs_object_id =/= csid. cs_object_id is the object record human readable
		# id whereas csid is the UUID for the record
		cs_object_id = rs_utils.filter_field_data_list(response,'accessionnumber')
		if cs_object_id:
			rs_item = cs_utils.fetch_cs_metadata(
				rs_item,
				rs_requester,
				cs_object_id,
				cs_requester
				)
			if rs_item.csid:
				return_value = {"Valid":True,"URL":rs_item.csid}
			else:
				return_value = {"Valid":"Invalid CSpace Object ID!","URL":rs_item.csid}

	return return_value

@app.post("/push_image/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, get the cspace object ID, and push the derivative to the CSpace record
# Note: this adds/updates the metadata from CSpace
async def push_image(cspace_instance,resource_id):
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	pushed = False
	return_value = {"Success":False}
	rs_item = rs_utils.RSpaceObject(rsid=resource_id)
	rs_requester = rs_utils.RSpaceRequest()
	cs_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	field_data = rs_requester.get_resource_field_data(resource_id=resource_id)
	# print(field_data)
	if field_data:
		# print([x for x in field_data if 'acc' in x])
		# print(cs_object_id)
		rsids = rs_utils.fetch_derivative_urls(rs_requester,resource_type,rsids=[],sinigle_rsid=resource_id)
		# i think this should iterate over rsids instead?? in case there's more than
		# one to push??
		item = rsids[0]
		rs_item.derivative_url = item['derivative url']
		cs_object_id = rs_utils.filter_field_data_list(field_data,'accessionnumber')
		if cs_object_id:
			# if it already has a csid, use it
			rs_item = cs_utils.fetch_cs_metadata(
				rs_item,
				rs_requester,
				cs_object_id,
				cs_requester
				)
			pushed = cs_utils.push_derivative(rs_item,cs_requester,rs_requester)
			return_value = {"Success":True}
		else:
			return_value = {"Success":f"Unable to push the derivative for {rs_item.rsid}!"}


	return return_value

@app.post("/push_image_group/{cspace_instance}/{resource_id}")
# using the resource id, query for the value (set in config.py?) in the RS record that will be used
# to define a "group" within RS. For example, reource 31 will have a "cinefiles_id"
# value of 60113, which is re-queried to form a "group" that will all have their
# derivatives pushed to the relevant cspace record
async def push_image_group(cspace_instance,resource_id):
	pass
