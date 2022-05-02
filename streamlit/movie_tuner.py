import json
import os

import streamlit as st
import requests
import google.auth.transport.requests
import google.oauth2.id_token
from typing import Dict
from google.oauth2 import service_account
import os


def _get_credentials(service_account_info, target_audience):
    return service_account.IDTokenCredentials.from_service_account_info(service_account_info,
                                                                        target_audience=target_audience)


def _get_service_account_info() -> Dict[str, str]:
    service_account_info_string = os.getenv("GCP_SERVICE_ACCOUNT") or st.secrets["GCP_SERVICE_ACCOUNT"]
    return json.loads(service_account_info_string)


def _get_auth_headers(audience) -> Dict[str, str]:
    credentials = _get_credentials(_get_service_account_info(), audience)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return {"Authorization": f"Bearer {credentials.token}"}


def invoke_function(message):
    url = "https://us-central1-pjd-hosting.cloudfunctions.net/similar-movies"
    return requests.post("https://us-central1-pjd-hosting.cloudfunctions.net/similar-movies",
                         json={"message": message},
                         headers=_get_auth_headers(audience=url))


st.title("Movie Tuner")

message = st.text_input("Message")
echo_message_response = invoke_function(message)

if echo_message_response:
    st.write(f"Your message is {echo_message_response.content}")
else:
    echo_message_response.raise_for_status()
