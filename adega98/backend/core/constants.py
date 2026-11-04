import os

# paths
ENVFILE_PATH = ".env"
FRONTEND_PATH = os.path.join("adega98", "frontend")
TEMPLATES_PATH = os.path.join(FRONTEND_PATH, "templates")
STATIC_PATH = os.path.join(FRONTEND_PATH, "static")
JS_PATH = os.path.join(STATIC_PATH, "js")
IMAGES_PATH = os.path.join(STATIC_PATH, "images")
CSS_PATH = os.path.join(STATIC_PATH, "css")
FONTS_PATH = os.path.join(STATIC_PATH, "fonts")
LOGS_PATH = "/logs"

# mensagens de erro
ENVFILE_NOT_FOUND = "envfile not found"
MISSING_ENV = "variable not found"
INVALID_RETURNS_TYPE = "the specified return type is not valid"
ALREADY_EXISTING_PRODUCT = "this product, with the same name, purchase and sale price, brand and validity already has registration"
PRICE_GREATER_ZERO = "the price must be a number greater than zero"
INVALID_LENGTH_NAME = "the name is too long or short"
INTERNAL_ERROR = "an internon error occurred"

# valores
MIN_LENGTH_PRODUCT_NAME = 3
MAX_LENGTH_PRODUCT_NAME = 30