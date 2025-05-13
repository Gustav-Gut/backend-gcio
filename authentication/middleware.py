class KongHeadersMiddleware:
    """
    Middleware para extraer headers HTTP_X_* de Kong,
    """
    EXEMPT_PATHS = (
        '/api/auth/login/',
        '/api/auth/refresh/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for path in self.EXEMPT_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)
            
        # Extraer los headers HTTP_X_* y asignarlos como atributos del request
        # (por ejemplo, HTTP_X_CLIENT_ID se convierte en request.client_id)
        for meta_key, value in request.META.items():
            if meta_key.startswith('HTTP_X_'):
                attr = meta_key[5:].lower().replace('-', '_')
                setattr(request, attr, value)

        return self.get_response(request)
