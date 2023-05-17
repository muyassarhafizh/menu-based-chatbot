# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import psycopg2
import datetime
import requests

url = 'http://185.32.161.60:40653/api/predict'

class DeliveryStatusQueryResponse(Action):
    def name(self) -> Text:
        return "delivery_status_query_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.latest_message['intent'].get('name')
        confidence = tracker.latest_message['intent'].get('confidence')
        
        message={}
        message["intent"]=intent
        message["confidence"]=confidence
        order_number = tracker.slots.get("order_number")
        
        if order_number:
            try:
                conn = psycopg2.connect(host="localhost", port="5432", dbname="postgres", user="postgres", password="Password11")
                cur = conn.cursor()

                # execute the query to retrieve the delivery status
                query = "SELECT delivery_status,delivery_time FROM food_delivery.delivery WHERE order_id = %s"
                cur.execute(query, (order_number,))
                data_retrieved = cur.fetchone() 
                try:
                    data_retrieved_list = list(zip([desc[0] for desc in cur.description],data_retrieved))
                except:
                    data_retrieved_list =[]

                db_retrieved = {}
                ##Fix datetime type of data
                for info in data_retrieved_list:
                    if isinstance(info[1], datetime.datetime):
                        value=info[1].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        value=info[1]
                    db_retrieved[info[0]]=value
                status = db_retrieved['delivery_status']

                additional_entity = {}
                for entity in tracker.latest_message["entities"]:
                    entity_type = entity["entity"]
                    entity_value = entity["value"]
                    additional_entity[entity_type] = entity_value
                
                message.update(db_retrieved)
                message.update(additional_entity)
                #Passsing parameters to API
                params = {
                        'text': f"tulis respons dengan informasi berikut: {str(message)}",
                        'top_p': 0.75,
                        'temperature': 0.4,
                        'max_length_tokens': 128,
                        'max_context_length_tokens': 2048
                        }
                
                headers = {'accept': 'application/json'}
                #delsoon
                dispatcher.utter_message(str(params))
                
                response = requests.post(url, params=params, headers=headers)
                if response.status_code == 200:
                    final_msg = response.json().replace("\'",'')
                else:
                    final_msg = f'Request failed with status code {response.status_code}.'

                if status:
                    dispatcher.utter_message(str(final_msg))
                else:
                    dispatcher.utter_message(str(final_msg))
            except Exception as e:
                # handle any errors that occur during the query
                dispatcher.utter_message(f"Unable to find order with the order number you provided: {order_number}")
                 
        else:
            dispatcher.utter_message("Sure, what's your order number?")
        return []



# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
