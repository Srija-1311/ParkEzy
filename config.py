"""
Configuration settings for Smart Parking System
"""
import os

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Upload settings
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model settings
    MODEL_PATH = 'models/yolov8n.pt'
    SLOTS_PATH = 'data/UFPR04/slots.json'
    
    # Detection settings
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
