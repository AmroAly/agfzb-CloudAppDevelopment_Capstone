import sys
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import requests
import os



def main(dict=None):

    try:
        client = Cloudant.iam(
            account_name=dict["COUCH_USERNAME"],
            api_key=dict["IAM_API_KEY"],
            url=dict['COUCH_URL'],
            connect=True,
        )
        my_result = {'rows': []}
        reviews_db = client["reviews"]
        if dict["__ow_method"] == 'get':
        
            if 'dealerId' in dict and dict['dealerId'].isnumeric():
                dealerId = int(dict['dealerId'])
                
                index = reviews_db.create_query_index(
                    design_document_id='query',
                    index_name='dealer_id',
                    fields=['dealership']
                )
            
                index.create()
                selector = {'dealership': {'$eq': dealerId}}
                docs = reviews_db.get_query_result(selector)
                
                for doc in docs:
                    my_result['rows'].append(doc)
            
            return my_result
        # handel post request
        if 'review' in dict:
            fields = ['id', 'name', 'dealership', 'review', 'purchase', 'another', 'purchase_date', 'car_make', 'car_model', 'car_year']
            for field in fields:
                if field  not in dict['review']:
                    return {"error": "All fields are required"}
            review = dict['review']
            for key, val in review.items():
                if val == "":
                    return {"error": "empty values are not allowed!"}
            reviews_db.create_document(review)
            return {"message": "Review has been created!"}
        return {"message": "Review is missing!"}  
        
    except CloudantException as ce:
        print("unable to connect")
        return {"error": ce}
   
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
            print("connection error")
            return {"error": err}