# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
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

class ActionHandleOptions(Action):

    def name(self) -> Text:
        return "action_handle_options"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # The default value is main
        submenu = tracker.get_slot("submenu")
        option2action_name =   {"main": {
                                    0: "action_restore_option",
                                    1: "action_handle_reservation",
                                    2: "action_handle_about_ismaya",
                                    3: "action_handle_help_center"},
                                "restaurant_name": {
                                    1: ("action_handle_reservation", "https://wa.me/6285921582888"),
                                    2: ("action_handle_reservation", "https://wa.me/6285710800003"),
                                    3: ("action_handle_reservation", "https://wa.link/2gignm"),
                                    4: ("action_handle_reservation", "https://wa.me/6287782961999"),
                                    5: ("action_handle_reservation", "https://wa.me/6281513153300"),
                                    6: ("action_handle_reservation", "https://wa.me/6281299073300"),
                                    7: ("action_handle_reservation", "https://wa.me/628111460838"),
                                    8: ("action_handle_reservation", "https://wa.me/6281808885404"),
                                    9: ("action_handle_reservation", "https://wa.me/6285817710002"),
                                    10: ("action_handle_reservation", "https://wa.me/6289670364055"),
                                    11: ("action_handle_reservation", "https://wa.me/6281113927276"),
                                    }
                                }
        try:
            option = int(tracker.get_slot("option"))
        except ValueError:
            dispatcher.utter_message(text=f"Tolong masukan angka!")
            return [SlotSet('option', None)]
        try:
            next_action = option2action_name[submenu][option]
        except KeyError:
            dispatcher.utter_message(text=f"Opsi ini tidak tersedia!")
            return [SlotSet('option', None)]

        dispatcher.utter_message(text=f"Kamu telah memilih opsi {option} !")

        if type(next_action) is tuple:
            return [SlotSet('option', None),
                    SlotSet('suboption', next_action[1]),
                    FollowupAction(name=next_action[0])]
        else:
            return [SlotSet('option', None),
                    FollowupAction(name=next_action)]

class ActionRestoreOption(Action):

    def name(self) -> Text:
        return "action_restore_option"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet('submenu', 'main'),
                SlotSet('suboption', None),
                FollowupAction(name='action_handle_reservation')]

# source of framework descriptions: https://marutitech.com/top-8-deep-learning-frameworks/
class ActionHandleReservation(Action):

    def name(self) -> Text:
        return "action_handle_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#        message = """Torch is a scientific computing framework that offers broad support for machine learning\n
#algorithms. It is a Lua based deep learning framework and is used widely amongst industry giants\n
#such as Facebook, Twitter, and Google."""
        suboption = tracker.get_slot("suboption")
        if suboption is None:
            # We are in the main menu
            message = """Silahkan pilih Outlet yang ingin Anda tuju :\n
            1. A/A dan A/O Bar\n
            2. Dragonfly\n
            3. Social Garden Senayan City\n
            4. Mr. Fox Jakarta\n
            5. Osteria Gia Pacific Place\n
            6. Osteria Gia Plaza Indonesia\n
            7. Osteria Gia Pondok Indah Mall 2\n
            8. Skye\n
            9. Social House\n
            10. Mr. Fox Surabaya\n
            11. Manarai Beach House"""

            dispatcher.utter_message(text=message)

            # Indicate the submenu in which the options below will be processed
            return [SlotSet('submenu', "restaurant_name")]
        else:
            # We are in a submenu
            message = """Silahkan klik link berikut untuk melakukan reservasi : {}\n
            Ketik 0 untuk kembali ke menu sebelumnya"""

            dispatcher.utter_message(text=message.format(suboption))

            # Indicate the submenu in which the options below will be processed
            return [SlotSet('submenu', "main"),
                    SlotSet('suboption', None)]

class ActionHandleAboutIsmaya(Action):

    def name(self) -> Text:
        return "action_handle_about_ismaya"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = """Silahkan tanyakan apa saja tentang ismaya"""
        dispatcher.utter_message(text=message)
        return []

class ActionHandleHelpCenter(Action):

    def name(self) -> Text:
        return "action_handle_help_center"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = """Mohon ketik 'agen' jika ingin berbicara dengan agen"""
        dispatcher.utter_message(text=message)


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
