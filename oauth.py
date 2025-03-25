import secrets
import streamlit as st
from streamlit_oauth import OAuth2Component

def generate_state():
    return secrets.token_urlsafe(16)

def google_login():
    try:
        # Get Google credentials from secrets
        CLIENT_ID = st.secrets.GOOGLE_OAUTH.client_id
        CLIENT_SECRET = st.secrets.GOOGLE_OAUTH.client_secret
        REDIRECT_URI = st.secrets.GOOGLE_OAUTH.redirect_uri


        # OAuth2 component
        oauth = OAuth2Component(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
        )
        
        
        result = oauth.authorize_button(
            name="Continue with Google",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google",
            extras_params={
            "prompt": "select_account",
            "nonce": generate_state(),
            },
        )

        return result
    except KeyError as e:
        st.error(f"Missing configuration: {e}. Check your secrets.toml file")
        st.stop()
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        st.stop()