
import json
import boto3
import decimal

# DynamoDB boto3 resource and variable
dynamodb = boto3.resource('dynamodb',region_name='us-west-2')

#Fill in the dynamo db table name that you have created in previous steps
loans_table_name = 'user-details-us-west-2-sahil'
table = dynamodb.Table(loans_table_name)

def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']

def get_named_property(event, name):
    return next(
        item for item in
        event['requestBody']['content']['application/json']['properties']
        if item['name'] == name)['value']
        
def getUserFinances(user_id):
    response = table.get_item(
                Key={'userid': user_id})
    
    return response['Item']      

def checkPMSEligibility(user_id):
    response = table.get_item(
                Key={'userid': user_id})
                
    investment = response['Item']['investments']
   
    print(investment)    
    
    if (investment > 50000):
        return {
            "response": {
                "userid": user_id,
                "PMSEligibility": True
            }
        }
    else:
        return {
            "response": {
                "userid": user_id,
                "PMSEligibility": False
            }
        }

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    if function == 'pms_eligibility':
        user_id = get_named_parameter(event, "userid")
        body = checkPMSEligibility(user_id)
        
    elif function == 'get_user_finances':
        user_id = get_named_parameter(event, "userid")
        body = getUserFinances(user_id)
        
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}
        
    response = str(body)
    responseBody = {"TEXT": {"body": json.dumps(response)}}
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
 
    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }

    }

    dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(dummy_function_response))

    return dummy_function_response
