import os
import streamlit as st


def get_ollama_models():
    """Get available Ollama models from the system"""
    try:
        model_options = os.popen("ollama list").read().splitlines()
        model_options = [m.split()[0] for m in model_options if m.strip() and not m.startswith("NAME")]
        model_options.append("Other")
        return model_options
    except:
        return ["Other"]


def is_ollama_available():
    """Check if Ollama is available on the system"""
    try:
        result = os.popen("ollama list").read()
        return bool(result)
    except:
        return False
