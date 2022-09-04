import json
import os

import streamlit as st
import requests
import google.auth.transport.requests
import google.oauth2.id_token
from typing import Dict
from google.oauth2 import service_account


def _get_credentials(service_account_info, target_audience):
    return service_account.IDTokenCredentials.from_service_account_info(service_account_info,
                                                                        target_audience=target_audience)


def _get_service_account_info() -> Dict[str, str]:
    return st.secrets["gcp_service_account"]


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


# TODO: script to load movie data into Data Store
# TODO: script to create unit vectors per movie (tf-idf?) (don't bother with tf-idf, all tags have identical frequency)
# TODO: cloud function trigger to add top 10/20 tags per movie
# TODO: cloud function trigger to add movie poster URL
# TODO: cloud function trigger to calculate movie similarity
# TODO: cloud function for movie search
# TODO: cloud function for movie GET
