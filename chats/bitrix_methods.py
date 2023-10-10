import json
import requests

USERS_LINK = "https://crmarea.carshauler.com/rest/141/oqd9g6q28n1ob2di/"
CRM_LINK = "https://crmarea.carshauler.com/rest/141/2qbsxatpawlsl6dp/"

def get_user_id_by_auth(auth):
    return json.loads(requests.post(USERS_LINK+"user.current", json={"auth":auth}).text)["result"]["ID"]

def tg_id_by_contact_id(contact_id):
    response = requests.post(CRM_LINK + "crm.contact.get", json={"id": contact_id})
    return json.loads(response.text)["result"]["UF_CRM_1687537511284"]