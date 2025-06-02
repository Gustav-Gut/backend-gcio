from .models import User

import logging
logger = logging.getLogger('follow_up.services')

class UserService:
    @staticmethod
    def get_info(user_rut: int):
        """
        Función base para obtener info del usuario.
        """
        return User.objects.filter(rut=user_rut)
