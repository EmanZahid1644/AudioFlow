import cloudinary
from cloudinary_config import *

print(cloudinary.config().cloud_name)