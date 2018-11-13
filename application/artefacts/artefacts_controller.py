from flask import current_app
import uuid
import datetime
from elasticsearch.exceptions import NotFoundError

def show(params): 
    if not current_app.es:
        return {"error":"search engine not available"}, 503
    try:
        result = current_app.es.get(
            index="artefacts",
            doc_type=params["type"],
            id=params["id"]
        )
        return result, 200
    except NotFoundError:
        return {"error":"not found"}, 404

def index(params):
    if not current_app.es:
        return {"error":"search engine not available"}, 503
    
    date_range = {
        "gte": params["date_range"]["start_date"],
        "lte": params["date_range"]["end_date"]
    } if "date_range" in params else {}

    result = current_app.es.search(
        index="artefact",
        doc_type=params["type"],
        body={
            "sort" : [
                "_score",
                { "created_at" : { "order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": date_range
                        }
                    },        
                    "should": {
                        "match": {"tags": params["search"]}
                    } 
                }   
            }
        })
    return result["hits"]["hits"], 200

def create(params):
    if not current_app.es:
        return {"error":"search engine not available"}, 503
    date = datetime.datetime.now().isoformat()
    return current_app.es.create(
        index="artefact", 
        doc_type=params["type"], 
        id=params["id"], 
        body={
            "tags": params["tags"], 
            "file_url": params["file_url"],
            "created_at": date
        }), 201

def update(params):
    if not current_app.es:
        return {"error":"search engine not available"}, 503
    
    update_params = {}
    if "tags" in params: update_params["tags"] = params["tags"] 
    if "image_url" in params: update_params["file_url"] = params["file_url"]

    try:
        current_app.es.update(
            index="artefact",
            doc_type=params["type"],
            id=params["id"],
            body={
                "doc" : update_params
            })
        return '', 204
    except NotFoundError:
        return {"error":"not found"}, 404     

def delete(params):
    if not current_app.es:
        return {"error":"search engine not available"}, 503
    try:
        current_app.es.delete(
            index="artefact",
            doc_type=params["type"],
            id=params["id"])
        return '', 204
    except NotFoundError:
        return {"error":"not found"}, 404     