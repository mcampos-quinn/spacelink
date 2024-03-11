# spacelink

linking cspace and resourcespace

`pip3 install "fastapi[all]"`

This will eventually be a simple API endpoint for urls called from the resourcespace UI. That will offer a few functions for realtime updates between RS and CS. For the moment I'm starting with a simpler script that will do the basics of a 2-way sync between CS and RS (data to RS and images to CS).


## Initial nightly sync script

Usage: `python3 nightlink.py MY_CSPACE_INSTANCE`

1) Query RS for new items, checking for a `synced?` field (value should be `True` or `Null`)

2) For each new RS item, grab an accession number from an auto-populated `accession number` field

3) Query CSpace using the accession number, returning metadata for the object

4) Add the metadata to the RS item, and also send a specified derivative size to
CSpace, creating `media` & `blob` records, then make a `relation` record linking them to the original object

5) If all is kosher, update the RS item with `synced=True`

## API endpoint flow

1) button is pushed on RS record view

2) triggers a POST request to specified URL, including RSID as a parameter

3) Use `RSID` and `query type` to query RS back and retrieve some relevant piece of metadata that will serve as a hook

4) Use this value from RS (i.e. `cspace object id` or `accession number`) to query CSpace again

5) Send CSpace response back to the item in RS


### from rs button

All queries just include RS number, but will also contain optional parameters in the URL. so:

query types:
 - `validate_cspace_id`
 - `push_image`
 - WIP: `push_image_group` (this will be used for pushing groups of images to cinefiles; for example its primary use will be to send an arbitrary number of stills to a single cspace record for a movie)

Other default options?? TBD
