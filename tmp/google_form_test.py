# %%
from google.oauth2 import service_account
from apiclient import discovery
import configparser

class GoogleFormApiAdapter:
    config = configparser.ConfigParser()
    config.read('config.txt')
    token_file  = config.get('GFORM', 'token_file', fallback='./GCP/tokens/token.json')
    credentials_file  = config.get('GFORM', 'credentials_file', fallback='./GCP/secret-key/credentials.json')
    CREATE_SCOPE = "https://www.googleapis.com/auth/forms.body"
    RESPONSE_SCOPE = "https://www.googleapis.com/auth/forms.responses.readonly"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_file,
        )
        self.form_service = discovery.build(
            "forms",
            "v1",
            credentials=creds,
            discoveryServiceUrl=self.DISCOVERY_DOC,
            static_discovery=False,
        )
    
    def create_new_form(self,title):
        NEW_FORM = {
            "info": {
                "title": title,
            }
        }
        result = self.form_service.forms().create(body=NEW_FORM).execute()
        print(result)
        return result
    
    def add_new_question(self,form_id,title,options):
        NEW_QUESTION = {
            "requests": [
                {
                    "createItem": {
                        "item": {
                            "title": (
                                "In what year did the United States land a mission on"
                                " the moon?"
                            ),
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {"value": "1965"},
                                            {"value": "1967"},
                                            {"value": "1969"},
                                            {"value": "1971"},
                                        ],
                                        "shuffle": True,
                                    },
                                }
                            },
                        },
                        "location": {"index": 0},
                    }
                }
            ]
        }
        return self.form_service.forms().batchUpdate(formId=form_id, body=NEW_QUESTION).execute()

    def get_response(self,form_id):
        get_result = self.form_service.forms().get(formId=form_id).execute()
        print(get_result)
        return get_result

if __name__ == "__main__":
    gfa = GoogleFormApiAdapter()
    result = gfa.create_new_form("test_form")
# %%
