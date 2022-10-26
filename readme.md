# spacelink

linking cspace and resourcespace

## FLOW:

1) button is pushed on rs record

2) triggers an async (AJAX?) GET request to specified URL, including RSID as a parameter

3) use the rsid and query type to query rs back

4) use rs arbitrary value (i.e. cspace object id) to query cspace again

5) send cspace response back to rs


### from rs button

all queries just include rs number, but will also contain optional parameters in the URL. so:

query_type:
 - validate-cspace-id
 - push-resource
 - retrieve-metadata [i.e. to add md to a blank record]
 - ??

### response to rs query

1) using the provided rsid and query_type (and whatever else?) query rs back to get the relevant values needed to query cspace

2) keep the rsid in a query object (?), query cspace to get desired data with the value retreived from rs, parse cspace XML response, get back desired cspace metadata

3) depending on query status from cspace, do stuff in rs
