import base64
import imghdr
import uuid

import six
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """ Поле для обработки изображений в формате Base64. """
    
    def to_internal_value(self, data):
        if data == '':
            return None
        
        if isinstance(data, six.string_types):
            if 'base64,' in data:
                data = data.split('base64,')[1]
            
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = file_name + "." + file_extension
            
            data = ContentFile(decoded_file, name=complete_file_name)
        
        return super(Base64ImageField, self).to_internal_value(data)
    
    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        if extension is None:
            raise serializers.ValidationError(
                "Не удалось определить формат файла."
            )
        extension = "jpg" if extension == "jpeg" else extension
        return extension
