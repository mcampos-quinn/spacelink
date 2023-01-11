"""
CONFIG SETTINGS
"""
import urllib

CSPACE_INSTANCE = {
	"art_collection": {
		"resource type":13,
		"fields_to_extract":{
			"rs field id":"cspace field tag name",
			# ~ ~ ~ NOTE!! this  might also need to be an XPath expression to get
			# at a nested tag. in the below example the cspace <dateDisplayDate> tag can exist
			# under any number of parent tag groups, so we have to specify which
			# one we actually want to retrieve
			"12":"objectProductionDateGroup//dateDisplayDate"
		},
		"query results per page":10,
		"cspace max query results":12,
		"cspace_services_url":"https://blabla/cspace-services/"
		}
	}
CSPACE_USER = ""
CSPACE_PASSWORD = ""
RS_URL = "https://bla/api/"
RS_USER = urllib.parse.quote_plus("yr mom")
RS_USERKEY = "bla"
# this is defined in RS as 'preview size', e.g. 'scr'
DERIVATIVE_SIZE = "scr"
