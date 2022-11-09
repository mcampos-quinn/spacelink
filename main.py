from fastapi import FastAPI
# local imports
import cs_utils
import rs_utils


app = FastAPI()

@app.post("/validate_cs_object_id/{cspace_instance}/{resource_id}")
# passing a cspace instance to the url (matching one set in config) and a
# resource_id, validate the cspace object ID entered within resourcespace metadata
async def validate_CSID(cspace_instance,resource_id):
	return_value = {"Valid":False,"URL":""}
	rspace_requester = rs_utils.RSpaceRequest()
	cspace_requester = cs_utils.CSpaceRequest(cspace_instance=cspace_instance)
	response = rspace_requester.get_resource_field_data(resource_id=resource_id)
	if response:
		data = response
	else:
		data = 'false'
	obj_no = rs_utils.filter_field_data_list(data,'acc')
	if obj_no:
		response = cspace_requester.run_query(
			cspace_service='collectionobjects',
			parameters=f"?as=collectionobjects_common:objectNumber='{obj_no}'"
			)
		csid,url = cspace_requester.parse_paged_response(response.text)
		if csid and url:
			return_value = {"Valid":True,"URL":url}

	return return_value


'''
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
