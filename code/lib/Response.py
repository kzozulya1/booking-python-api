from flask import json, Response

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  response = Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
  response.headers['Access-Control-Allow-Origin'] = '*'
  return response
  
"""  
def options_response(status_code):
  res = {};
  response = Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, api-token'
  response.headers['Access-Control-Allow-Methods'] = 'PUT'
  
  
  return response  
"""