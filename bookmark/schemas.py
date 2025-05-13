from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import BookmarkSerializer

# Esquema para list_bookmarks
list_bookmarks_schema = {
    "summary": "List user bookmarks",
    "description": "Retrieves all active bookmarks for a user, including their related actions",
    "parameters": [
        OpenApiParameter(
            name="external_source_id",
            description="External Source ID (UUID) to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="client_id",
            description="Client ID to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="status",
            description="Status to filter bookmarks by (true/false)",
            required=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="action_id",
            description="Action ID (UUID) to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="category",
            description="Category of action to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="result",
            description="Result of action to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page",
            description="Page number for pagination",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page_size",
            description="Number of items per page (max: 100)",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY
        ),
    ],
    "responses": {
        200: OpenApiTypes.OBJECT,
    },
    "examples": [
        OpenApiExample(
            "Success Response",
            value={
                 "links": {
                    "count": 1,
                    "next": "next_page_url",
                    "previous": "previous_page_url"
                },
                 "data": [
                            {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Example Bookmark",
                            "url": "https://example.com",
                            "client_id": "12345678",
                            "created_at": "2023-05-20T15:30:45Z",
                            "updated_at": "2023-05-21T10:15:22Z",
                            "action": {  
                                "id": "456",
                                "category": "Category",
                                "result": "Result",
                                "icon": "icon-name",
                                "color": "#FFF",
                                "status": True
                            }  
                            }
                        ]  
            },
            response_only=True,
        )
    ]
}

# Esquema para create_bookmark
create_bookmark_schema = {
    "summary": "Create a new bookmark",
    "description": "Creates a new bookmark and returns its ID ",
    "request": BookmarkSerializer,
    "responses": {
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    "examples": [
        OpenApiExample(
            "Request Example",
            value={
                "url": "https://example.com",
                "title": "New Bookmark",
                "client_id": "12345678", # Campo obligatorio
                "external_source_id": "123e4567-e89b-12d3-a456-426614174002", # Campo obligatorio
                "action_id": "123e4567-e89b-12d3-a456-426614174003", # Campo obligatorio
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={
                "id": "123"
            },
            response_only=True,
        )
    ]
}

# Esquema para update_bookmark
update_bookmark_schema = {
    "summary": "Update a bookmark",
    "description": "Updates specified fields of an existing bookmark",
    "parameters": [
        OpenApiParameter(
            name="id",
            description="Bookmark ID (UUID)",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH
        ),
    ],
    "request": BookmarkSerializer,
    "responses": {
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    "examples": [
        OpenApiExample(
            "Request Example",
            value={
                "title": "Updated Title",
                "url": "https://updated-example.com",
                "status": True,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={
                "message": "Bookmark updated successfully"
            },
            response_only=True,
        )
    ]
}

# Esquema para delete_bookmark
delete_bookmark_schema = {
    "summary": "Toggle bookmark status",
    "description": "Activates or deactivates a bookmark (toggles status). Requires both bookmark ID and external source ID to ensure proper authorization.",
    "parameters": [
        OpenApiParameter(
            name="id",
            description="ID of the bookmark to toggle",
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="external_source_id",
            description="External Source ID (UUID) to verify bookmark ownership",
            required=True,
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY
        )
    ],
    "responses": {
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT
    },
    "examples": [
        # Ejemplos para solicitudes
        OpenApiExample(
            "Valid Request Query Params",
            value={
                "id": "123",
                "external_source_id": "550e8400-e29b-41d4-a716-446655440000"
            },
            request_only=True,
            description="Parámetros de consulta válidos para alternar el estado de un bookmark"
        ),
        
        # Ejemplos para respuestas exitosas
        OpenApiExample(
            "Bookmark Activated",
            value={"message": "Bookmark activated"},
            response_only=True,
            status_codes=["200"],
            description="Cuando un bookmark inactivo se activa"
        ),
        OpenApiExample(
            "Bookmark Deactivated",
            value={"message": "Bookmark deactivated"},
            response_only=True,
            status_codes=["200"],
            description="Cuando un bookmark activo se desactiva"
        ),
        
        # Ejemplos para errores de validación
        OpenApiExample(
            "Missing Bookmark ID",
            value={"error": "Bookmark ID is required"},
            response_only=True,
            status_codes=["400"],
            description="Cuando no se proporciona el ID del bookmark"
        ),
        OpenApiExample(
            "Missing External Source ID",
            value={"error": "External Source ID is required"},
            response_only=True,
            status_codes=["400"],
            description="Cuando no se proporciona el ID de la fuente externa"
        ),
        OpenApiExample(
            "Invalid UUID Format",
            value={"error": "external_source_id must be a valid UUID format"},
            response_only=True,
            status_codes=["400"],
            description="Cuando el formato del UUID de external_source_id es inválido"
        ),
        
        # Ejemplo para error de autorización
        OpenApiExample(
            "Authorization Error",
            value={"error": "Bookmark does not belong to the specified external source"},
            response_only=True,
            status_codes=["403"],
            description="Cuando el bookmark no pertenece a la fuente externa especificada"
        ),
        
        # Ejemplo para error de recurso no encontrado
        OpenApiExample(
            "Bookmark Not Found",
            value={"error": "Bookmark not found"},
            response_only=True,
            status_codes=["404"],
            description="Cuando el bookmark especificado no existe"
        ),
        
        # Ejemplo para error del servidor
        OpenApiExample(
            "Server Error",
            value={"error": "An error occurred while processing your request"},
            response_only=True,
            status_codes=["500"],
            description="Cuando ocurre un error interno del servidor"
        )
    ]
}
# Esquema para by_source
list_bookmarks_by_source_schema = {
    "summary": "List bookmarks by external source",
    "description": "Retrieves all bookmarks for a specific external source with optional filtering",
    "parameters": [
        OpenApiParameter(
            name="external_source_id",
            description="External Source ID (UUID) to filter bookmarks by",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="client_id",
            description="Client ID to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="status",
            description="Status to filter bookmarks by (true/false)",
            required=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="action_id",
            description="Action ID (UUID) to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="category",
            description="Category of action to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="result",
            description="Result of action to filter bookmarks by",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page",
            description="Page number for pagination",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page_size",
            description="Number of items per page (max: 100)",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY
        ),
    ],
    "responses": {
        200: OpenApiTypes.OBJECT,
    },
    "examples": [
         OpenApiExample(
            "Success Response",
            value={
                 "links": {
                    "count": 1,
                    "next": "next_page_url",
                    "previous": "previous_page_url"
                },
                 "data": [
                            {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Example Bookmark",
                            "url": "https://example.com",
                            "client_id": "12345678",
                            "created_at": "2023-05-20T15:30:45Z",
                            "updated_at": "2023-05-21T10:15:22Z",
                            "action": {  
                                "id": "456",
                                "category": "Category",
                                "result": "Result",
                                "icon": "icon-name",
                                "color": "#FFF",
                                "status": True
                            }  
                            }
                        ]  
            },
            response_only=True,
        )
    ]
}
