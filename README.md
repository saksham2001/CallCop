# CallCop

Made by Saksham Bhutani, Shobhit Tulshain, Sakshi Parikh & P Ajay Venkatesh.

CallCop is a project that aims to detect fraudulent phone calls using AI. It uses a combination of Twilio's API, Large Language Models, and Firebase's API to detect fraudulent phone calls.

## Description

Our project focuses on real-time fraud detection using Twilio, Google API, and an ML model. When an unknown caller contacts a user, a Twilio agent joins the call, listening to the conversation. Using Twilio's API, we obtain real-time audio converted to text through Google's speech-to-text API. Our machine learning model then analyzes this transcription to determine if the caller is engaging in fraudulent or suspicious activities. If fraud is detected, the Twilio agent alerts the user during the call.

In scope of this solution are the seamless integration of Twilio for call handling, Google's API for real-time speech transcription, and the machine learning model for detecting fraudulent behaviour during the call. The solution focuses on detecting fraud in real-time through live transcription and analysis.

Out of scope includes any manual investigation of fraud after the call has ended, complex multi-lingual support beyond the languages handled by Google's API, and the creation of a detailed user interface beyond basic alerts. We also exclude handling fraud detection outside of phone conversations, such as in emails or messages.

Future opportunities for the solution include expanding to support more languages and dialects, integrating biometric or voice recognition to improve fraud detection accuracy, and developing advanced features like getting to know about the latest scams with the help of new channels api’s to refine the model’s capabilities further. Additionally, expanding the system to other communication channels such as SMS or email is another possibility for the future.


# Web server

The web server is a Flask application that uses the Twilio API to handle phone calls and the LLM API to detect fraudulent phone calls.

## Installation

1. Clone the repository
2. Install the dependencies (pip install -r requirements.txt)
3. Run the server (python twilio_live.py)

## Usage

1. Clone the repository
2. Install the dependencies (pip install -r requirements.txt)
3. Run the server (python app.py)

# Flutter App

The Flutter app is a mobile application.

## Installation

1. Clone the repository
2. Install the dependencies (flutter pub get)
3. Run the app (flutter run)