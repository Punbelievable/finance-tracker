# finance-tracker

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Firebase](https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black)

---

## Features

- **Secure Login**: Use Google OAuth for fast and secure authentication.
- **Add Transactions**: Easily record your financial transactions.
- **Transaction History**: View a detailed history of all your transactions.
- **Data Visualization**: Analyze your finances with simple pie charts and line graphs.

---

## Installation

Get started by setting up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Punbelievable/finance-tracker.git
2. **Navigate to the Directory**:
   ```bash
   cd finance-tracker
3. **Install Dependencies**:
   ```bash
   pip install streamlit pandas matplotlib google-auth firebase-admin streamlit-oauth

---

## Usage
1. **Launch the App**:
   ```bash
   streamlit run app.py
   
2. **Log In**: Click the login button to authenticate with your Google account.
3. **Add Transactions**: Input your transaction details and submit them.
4. **View History**: Check your past transactions in the history section.
5. **Explore Stats**: Visualize your financial data with charts and graphs.

---
# Configuration
To get the app fully functional, you’ll need to configure **Firebase** and **Google OAuth**. You’ll also need to create a *secrets.toml* file in the *.streamlit* folder to store sensitive credentials.

- **Firebase Setup**:
  - Create a Firebase project at [Firebase](https://firebase.google.com/).
  - Enable Firestore and Google Authentication in the Firebase console.
  - Download the service account key and place it in the project directory.
  - Update the [firebase] section in *secrets.toml* with your credentials (see template below).

  
- **Google OAuth Setup**:
  - Visit the [Google Cloud Console](https://console.cloud.google.com/) to set up OAuth credentials.
  - Create a new OAuth client ID and note your client ID and secret.
  - Add these details to the [GOOGLE_OAUTH] section in secrets.toml (see template below).

**Creating the secrets.toml File**
Create a *.streamlit* folder in your project directory if it doesn’t already exist, then add a file named *secrets.toml* inside it. Copy the template below and replace the placeholders with your actual credentials:

```plaintext
finance-tracker/
├── .streamlit/
│   └── secrets.toml
├── ...
```

Copy the template below into **secrets.toml** and replace the placeholders with your actual credentials:
```toml
[GOOGLE_OAUTH]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
redirect_uri = "http://localhost:8501"
# For production, use: redirect_uri = "https://your-app-name.streamlit.app"

[firebase]
type = "service_account"
project_id = "your-firebase-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-client-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-x509-cert-url"
```

**Note**: Replace placeholders like your-google-client-id, your-firebase-project-id, etc., with your actual values from Firebase and Google Cloud Console.


---
## Technologies Used

- Streamlit: For the interactive web interface.
- Pandas: For data manipulation and analysis.
- Matplotlib: For creating pie charts and line graphs.
- Firebase: For Firestore database and authentication (via Google).


---
**Contributing**
Love the project? Contributions are welcome! Feel free to:

1. Fork the repository.
2. Make your improvements.
3. Submit a pull request.
   
   
