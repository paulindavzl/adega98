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
LOGS_PATH = os.path.join("logs")
BACKEND_PATH = os.path.join("adega98", "backend")
FILES_PATH = os.path.join(BACKEND_PATH, "files")
PRODUCT_FILES_PATH = os.path.join(FILES_PATH, "products")

# mensagens de erro
ENVFILE_NOT_FOUND = "envfile not found"
MISSING_ENV = "variable not found"
INVALID_RETURNS_TYPE = "the specified return type is not valid"
ALREADY_EXISTING_PRODUCT = "this product, with the same name, purchase and sale price, brand and validity already has registration"
PRICE_GREATER_ZERO = "the price must be a number greater than zero"
INVALID_LENGTH_NAME = "the name is too long or short"
INTERNAL_ERROR = "an internon error occurred"
EXCEPTION_NOT_INTERNAL_BASE = "the exception passed not an internal system base (Adega98Exception)"
LOGS_NOT_DEFINED = "a Logs class was not added"
INVALID_GET_ALL_PRODUCT_SELECT = "column for invalid product selection"
PRODUCT_IDENTIFIER_CANNOT_NONE = "the product identifier or identification value cannot be None"
INVALID_PRODUCT_IDENTIFIER = "invalid product identifier"
INVALID_PRODUCT_IDENTIFIER_VALUE = "the product identifier given is invalid"
PRODUCT_NOT_FOUND = "the product sought was not found"
INVALID_IMAGE_EXTENSION = "the image extension is invalid"
IMAGE_WITHOUT_CONTENT = "the uploaded image file has no content"
MAX_IMAGE_SIZE_EXCEEDED = "the image exceeds the maximum allowed size"
INVALID_IMAGE = "the image is invalid"
UNKNOWN_USER_UPDATER = "it is not possible to update with an unknown user"


# valores
MIN_LENGTH_PRODUCT_NAME = 3
MAX_LENGTH_PRODUCT_NAME = 30
IMAGE_ALLOWEDS_EXTENSIONS = ["JPEG", "JPG", "PNG"]
MAX_IMAGE_SIZE_EXT_MB = 5
MAX_IMAGE_SIZE = MAX_IMAGE_SIZE_EXT_MB * 1024 * 1024
IMAGE_DIMENSION_PIXELS = (800, 800)