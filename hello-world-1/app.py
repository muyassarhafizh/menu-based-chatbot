"""
A sample Hello World server.
"""
import os
import requests
from flask_restful import Api, Resource

from flask import Flask, render_template,jsonify

app = Flask(__name__)
api = Api(app)

class HitRasa(Resource):
    def post(self,message):
        response = requests.post('https://5a84-103-125-37-137.ngrok-free.app/webhooks/rest/webhook', json={"message":message})
        response_final =response.json()[0]['text']
        return {"bot": response_final}

api.add_resource(HitRasa, "/hitrasa/<string:message>")

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
