import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st


def initialize_firebase():
    if not firebase_admin._apps:
        
        firebase_config = {
            "type": st.secrets.firebase.type,
            "project_id": st.secrets.firebase.project_id,
            "private_key_id": st.secrets.firebase.private_key_id,
            "private_key": st.secrets.firebase.private_key.replace('\\n', '\n'),
            "client_email": st.secrets.firebase.client_email,
            "client_id": st.secrets.firebase.client_id,
            "auth_uri": st.secrets.firebase.auth_uri,
            "token_uri": st.secrets.firebase.token_uri,
            "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
            "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url
        }
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()