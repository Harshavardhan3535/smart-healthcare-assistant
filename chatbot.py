import sys
import os
import json
import requests
import nltk
import time
from nltk.tokenize import word_tokenize

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ModuleNotFoundError:
    TRANSLATOR_AVAILABLE = False

try:
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ModuleNotFoundError:
    TENSORFLOW_AVAILABLE = False

def check_multiprocessing():
    """Check if _multiprocessing is available without using subprocess."""
    try:
        import _multiprocessing
        print("\u2705 _multiprocessing module is available.")
    except ImportError:
        print("\u274C _multiprocessing module not found. Consider reinstalling Python if needed.")

def ensure_nltk():
    """Ensure that NLTK and required datasets are available."""
    try:
        nltk.data.find('tokenizers/punkt')
        print("\u2705 'punkt' dataset is already available.")
    except LookupError:
        print("\u274C 'punkt' dataset not found. Downloading...")
        nltk.download('punkt')

def translate_text(text, target_lang='en'):
    """Translate text to the target language if translator is available."""
    if TRANSLATOR_AVAILABLE:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    return text

def detect_language(text):
    """Detects the language of the user's input if translator is available."""
    if TRANSLATOR_AVAILABLE:
        return GoogleTranslator().detect(text)
    return 'en'

def chatbot_response(user_input):
    """Healthcare chatbot that provides symptoms, causes, and tablet suggestions for various health issues."""
    detected_language = detect_language(user_input)
    user_input = translate_text(user_input, 'en').lower()
    health_issues = {
        "fever": {"symptoms": "High temperature, chills, sweating.", "cause": "Viral/bacterial infections, inflammation.", "medication": "Paracetamol, Ibuprofen."},
        "cough": {"symptoms": "Dry or wet cough, throat irritation.", "cause": "Colds, flu, allergies, infections.", "medication": "Dextromethorphan, Honey cough syrup."},
        "headache": {"symptoms": "Pain in the head, sensitivity to light, dizziness.", "cause": "Stress, dehydration, migraines.", "medication": "Acetaminophen, Ibuprofen."},
        "stomach pain": {"symptoms": "Cramping, bloating, nausea.", "cause": "Indigestion, ulcers, food poisoning.", "medication": "Antacids, Omeprazole."},
        "sore throat": {"symptoms": "Pain, dryness, difficulty swallowing.", "cause": "Viral infections, irritation.", "medication": "Lozenges, Ibuprofen."},
        "fatigue": {"symptoms": "Weakness, lack of energy, dizziness.", "cause": "Lack of sleep, anemia, stress.", "medication": "Multivitamins, Iron supplements."},
        "skin rash": {"symptoms": "Redness, itching, swelling.", "cause": "Allergies, infections, irritants.", "medication": "Antihistamines, Hydrocortisone cream."},
        "diabetes": {"symptoms": "Frequent urination, thirst, fatigue, blurry vision.", "cause": "Insulin resistance, high sugar levels.", "medication": "Metformin, Insulin (if prescribed)."},
        "allergies": {"symptoms": "Sneezing, runny nose, rashes, itchy eyes, difficulty breathing in severe cases.", "cause": "Pollen, dust, food allergies.", "medication": "Antihistamines, Cetirizine."},
        "breathing problems": {"symptoms": "Shortness of breath, wheezing, chest tightness.", "cause": "Asthma, allergies, respiratory infections.", "medication": "Inhalers, Bronchodilators."}
    }
    
    for issue, details in health_issues.items():
        if issue in user_input:
            response = f"Symptoms: {details['symptoms']} Causes: {details['cause']} Recommended medication: {details['medication']} I will check back with you in a week to see how you're doing."
            return translate_text(response, detected_language)
    
    return translate_text("I'm sorry, I don't have information on that. Please consult a healthcare professional for an accurate diagnosis and medication.", detected_language)

def analyze_health_image(img_path):
    """Analyze a health-related image and provide a diagnosis."""
    if not TENSORFLOW_AVAILABLE:
        return "Error: TensorFlow is not installed. Please install it using pip install tensorflow."
    
    try:
        model = MobileNetV2(weights='imagenet')
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        predictions = model.predict(img_array)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
        
        response = "Possible health conditions based on image:\n"
        for pred in decoded_predictions:
            response += f"- {pred[1]} ({round(pred[2] * 100, 2)}% confidence)\n"
        
        return response
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def chatbot_loop():
    """Simulated chatbot loop for restricted environments."""
    print("Welcome to the AI Healthcare Assistant!")
    test_questions = [
        "I have a fever, what should I do?",
        "How do I treat a cough?",
        "What are symptoms of diabetes?",
        "What are common allergy symptoms?",
        "I have breathing problems, what should I do?"
    ]
    
    user_follow_ups = {}
    
    for question in test_questions:
        print(f"You: {question}")
        response = chatbot_response(question)
        print(f"AI Assistant: {response}\n")
        user_follow_ups[question] = time.time()
    
    print("AI Assistant: I will check back in a week regarding your health status.")
    
    img_path = "sample_health_image.jpg"
    if os.path.exists(img_path):
        print("AI Assistant: Analyzing uploaded image...")
        print(analyze_health_image(img_path))
    else:
        print("AI Assistant: No image found for analysis.")

if name == "main":
    check_multiprocessing()
    ensure_nltk()
    chatbot_loop()