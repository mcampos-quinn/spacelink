from fastapi import FastAPI
# local imports
import config
import cs_utils
import rs_utils

app = FastAPI()

@app.post("/validate_cs_object_id/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, validate the cspace object ID entered within resourcespace metadata
async def validate_cs_object_id(cspace_instance,resource_id):
	return_value = {"Valid":False,"URL":""}
	rspace_requester = rs_utils.RSpaceRequest()
	cspace_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	response = rspace_requester.get_resource_field_data(resource_id=resource_id)
	if response:
		data = response
		obj_no = rs_utils.filter_field_data_list(data,'acc')
		if obj_no:
			response = cspace_requester.run_query(
				cspace_service='collectionobjects',
				parameters=f"?as=collectionobjects_common:objectNumber='{obj_no}'"
				)
			csid,url = cs_utils.parse_paged_response(response.text)
			if csid and url:
				# @FIXME set this field id in config too
				# update the rs record with the cs object url
				rspace_requester.update_field(resource_id=resource_id,field_id="107",value=url)

				return_value = {"Valid":True,"URL":url}

	return return_value

@app.post("/push_image/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, get the cspace object ID, and push the derivative to the CSpace record
async def push_image(cspace_instance,resource_id):
	resource_type = config.CSPACE_INSTANCE[cspace_instance]['resource type']
	pushed = False
	return_value = {"Success":False,"URL":""}
	rs_item = rs_utils.RSpaceObject(rsid=resource_id)
	rspace_requester = rs_utils.RSpaceRequest()
	cspace_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	# item_data = rspace_requester.do_search()
	field_data = rspace_requester.get_resource_field_data(resource_id=resource_id)
	# print(field_data)
	if field_data:
		# print([x for x in field_data if 'acc' in x])
		# print(cs_object_id)
		rsids = rs_utils.fetch_derivative_urls(rspace_requester,resource_type,rsids=[],sinigle_rsid=resource_id)
		item = rsids[0]
		rs_item.derivative_url = item['derivative url']
		cs_object_id = rs_utils.filter_field_data_list(field_data,'acc')
		if cs_object_id:
			# if it already has a csid, use it
			rs_item = cs_utils.fetch_cs_metadata(
				rs_item,
				rspace_requester,
				cs_object_id,
				cspace_requester
				)
			pushed = cs_utils.push_derivative(rs_item,cspace_requester,rspace_requester)

	return pushed




'''
run local dev server:
$ uvicorn main:app --reload

FLOW:
1) button is pushed on rs record
2) triggers an async (AJAX?) GET request to specified URL, including RSID as a parameter
3) this

***
from rs button: all queries just include rs number, but will also contain optional parameters in the URL. so:

query_type:
 - validate-cspace-id
 - push-resource
 - retrieve-metadata [i.e. to add md to a blank record]
 - ??

***


'''
