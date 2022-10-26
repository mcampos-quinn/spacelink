from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
