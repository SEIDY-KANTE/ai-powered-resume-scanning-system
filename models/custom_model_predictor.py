import os
import json
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import numpy as np

from config.constants import MODELS_OUTPUT_DIR

# --- Constants and Globals ---
LSTM_MODEL_FILENAME = "lstm_resume_matcher_model.keras"
LSTM_TOKENIZER_FILENAME = "lstm_tokenizer.json"
LSTM_MODEL_PATH = os.path.join(MODELS_OUTPUT_DIR, LSTM_MODEL_FILENAME)
LSTM_TOKENIZER_PATH = os.path.join(MODELS_OUTPUT_DIR, LSTM_TOKENIZER_FILENAME)

TRANSFORMER_MODEL_DIR = "transformer_resume_matcher_model"
TRANSFORMER_MODEL_PATH = os.path.join(MODELS_OUTPUT_DIR, TRANSFORMER_MODEL_DIR)

MAX_SEQUENCE_LENGTH_RESUME_LSTM = 500
MAX_SEQUENCE_LENGTH_JOB_LSTM = 500

_loaded_lstm_model = None
_loaded_lstm_tokenizer = None
_loaded_transformer_model = None
_loaded_transformer_tokenizer = None
_transformer_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- LSTM ---
def load_lstm_model_and_tokenizer():
    global _loaded_lstm_model, _loaded_lstm_tokenizer

    if _loaded_lstm_model is None:
        if os.path.exists(LSTM_MODEL_PATH):
            try:
                _loaded_lstm_model = tf.keras.models.load_model(LSTM_MODEL_PATH)
                print("LSTM model loaded.")
            except Exception as e:
                print(f"Failed to load LSTM model: {e}")
                return False
        else:
            print(f"LSTM model file not found at: {LSTM_MODEL_PATH}")
            return False

    if _loaded_lstm_tokenizer is None:
        if os.path.exists(LSTM_TOKENIZER_PATH):
            try:
                with open(LSTM_TOKENIZER_PATH, 'r', encoding='utf-8') as f:
                    tokenizer_data = f.read()
                    _loaded_lstm_tokenizer = tokenizer_from_json(tokenizer_data)
                print("LSTM tokenizer loaded.")
            except Exception as e:
                print(f"Failed to load LSTM tokenizer: {e}")
                return False
        else:
            print(f"LSTM tokenizer file not found at: {LSTM_TOKENIZER_PATH}")
            return False

    return True

def predict_with_lstm(resume_text, job_text):
    if not load_lstm_model_and_tokenizer():
        print("LSTM model/tokenizer not available.")
        return None

    try:
        resume_seq = _loaded_lstm_tokenizer.texts_to_sequences([resume_text])
        job_seq = _loaded_lstm_tokenizer.texts_to_sequences([job_text])

        resume_padded = pad_sequences(resume_seq, maxlen=MAX_SEQUENCE_LENGTH_RESUME_LSTM, padding='post', truncating='post')
        job_padded = pad_sequences(job_seq, maxlen=MAX_SEQUENCE_LENGTH_JOB_LSTM, padding='post', truncating='post')

        prediction = _loaded_lstm_model.predict([resume_padded, job_padded], verbose=0)
        return float(np.clip(prediction[0][0] * 100.0, 0.0, 100.0))
    except Exception as e:
        print(f"LSTM prediction error: {e}")
        return None

# --- Transformer ---
def load_transformer_model_and_tokenizer():
    global _loaded_transformer_model, _loaded_transformer_tokenizer

    if not os.path.exists(TRANSFORMER_MODEL_PATH):
        print(f"Transformer model directory not found at {TRANSFORMER_MODEL_PATH}")
        return False

    if _loaded_transformer_model is None:
        try:
            _loaded_transformer_model = DistilBertForSequenceClassification.from_pretrained(TRANSFORMER_MODEL_PATH)
            _loaded_transformer_model.to(_transformer_device)
            _loaded_transformer_model.eval()
            print(f"Transformer model loaded on device: {_transformer_device}")
        except Exception as e:
            print(f"Transformer model load error: {e}")
            return False

    if _loaded_transformer_tokenizer is None:
        try:
            _loaded_transformer_tokenizer = DistilBertTokenizerFast.from_pretrained(TRANSFORMER_MODEL_PATH)
            print("Transformer tokenizer loaded.")
        except Exception as e:
            print(f"Transformer tokenizer load error: {e}")
            return False

    return True

def predict_with_transformer(resume_text, job_text):
    if not load_transformer_model_and_tokenizer():
        print("Transformer model/tokenizer not available.")
        return None

    try:
        combined = resume_text + " [SEP] " + job_text
        inputs = _loaded_transformer_tokenizer(combined, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(_transformer_device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = _loaded_transformer_model(**inputs)
            score = outputs.logits.item()
            return float(np.clip(score * 100.0, 0.0, 100.0))
    except Exception as e:
        print(f"Transformer prediction error: {e}")
        return None
