# spacelink

linking cspace and resourcespace

`pip3 install "fastapi[all]"`

This will eventually be a simple API endpoint for urls called from the resourcespace UI. That will offer a few functions for realtime updates between RS and CS. For the moment I'm starting with a simpler script that will do the basics of a 2-way sync between CS and RS (data to RS and images to CS).


## Initial nightly sync script

Usage: `python3 nightlink.py MY_CSPACE_INSTANCE`

1) query rs for new items, using a 'synced' field (true/false, default of null)

2) get an accession number from the filename or from an auto-populated accession
	number field, TBD

3) Query cspace using the accession number, returning metadata for the object

4) Add the metadata to the RS item, and also send a specified derivative size to
	CS, creating media & blob records, then a relation record to the original
	object

5) If all is kosher, update the RS item with synced=true

## API endpoint flow

1) button is pushed on rs record view

2) triggers a POST request to specified URL, including RSID as a parameter

3) use the rsid and query type to query rs back and retrieve some relevant piece of metadata

4) use rs arbitrary value (i.e. "cspace object id/accession number") to query cspace again

5) send cspace response back to rs


### from rs button

all queries just include rs number, but will also contain optional parameters in the URL. so:

query_types:
 - validate-cspace-id
 - push-resource
 - retrieve-metadata [i.e. to add md to a blank record]
 - ??

Other default options??

### response to rs query

1) using the provided rsid and query_type (and whatever else?) this endpoint will trigger a query back to rs to fetch the relevant values needed to query cspace; the initial API call here creates a RSpaceObject where the data will be stored during the rest of the transaction

2) query cspace (using the data nugget from step 1) to get metadata for a single collection object, and add the relevant fields to the original item in a callback to RS.

_OR_

3) depending on query status from cspace, do other stuff in rs
