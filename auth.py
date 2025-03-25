from google.oauth2 import id_token
from google.auth.transport import requests
import streamlit as st

# Authenticate user using Google OAuth
# Returns user email if successful, None otherwise
def authenticate_user(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            st.secrets.GOOGLE_OAUTH.client_id
        )
        
        
        return {
            'info': idinfo,
            'email': idinfo['email'],
            'name': idinfo.get('name', 'User'),
            'picture': idinfo.get('picture', '')
        }
    
    except ValueError as e:
        st.error(f"Authentication failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None