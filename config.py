import os

class Config:
    # Default Provider Settings
    DEFAULT_PROVIDER = "ollama"
    
    # Ollama Settings
    OLLAMA_BASE_URL = "http://localhost:11434/v1"
    OLLAMA_MODEL = "llama3.2"
    
    # Nebius Settings (Base URL usually OpenAI compatible)
    NEBIUS_BASE_URL = "https://api.studio.nebius.ai/v1/" # Example, verify correct endpoint
    NEBIUS_MODEL = "google/gemma-2-2b-it" # Example high-quality model
    NEBIUS_API_KEY = "v1.CmQKHHN0YXRpY2tleS1lMDBiNnpzeGJuanJ3N2F6bXMSIXNlcnZpY2VhY2NvdW50LWUwMGFrOTIzODR0NjdzcGt4bjIMCIWR48oGEKTujY4DOgwIhZT7lQcQwIfHowFAAloDZTAw.AAAAAAAAAAHx5bY13HGXiox16ATVGN6dliOeSk2nIS67hirLS3DOfOByD76lV7pbjMSqyeWpa-wweliporRhm2kTYpXvhLgI"
    
    # Database
    DB_PATH = "jobs.sqlite"
