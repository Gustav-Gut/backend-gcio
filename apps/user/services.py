from .models import User

import logging
logger = logging.getLogger('follow_up.services')

class UserService:
    @staticmethod
    def get_info(user_rut: str):
        """
        Obtiene la información de un usuario por su RUT.

        Args:
            user_rut (str): RUT del usuario

        Returns:
            User: Instancia del usuario
        """
        return User.objects.get(rut=user_rut)
