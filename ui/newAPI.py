import requests
import os
from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class HitRasa(Resource):
    def post(self):
        json_data = request.get_json()
        message = json_data.get('message')
        response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"message":message})
        response_final =response.json()[0]['text']
        return {"bot": response_final}

api.add_resource(HitRasa, "/hitrasa")
    
if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8069')
    app.run(debug=True,port=server_port, host='0.0.0.0')
