class BookmarkValidationService:
    @staticmethod
    def validate_user_id(user_id):
        """Valida si el ID de usuario es válido"""
        return user_id is not None and isinstance(user_id, str) and user_id.strip() != ""
