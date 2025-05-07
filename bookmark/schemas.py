from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import BookmarkSerializer

# Esquema para list_bookmarks
list_bookmarks_schema = {
    "summary": "List user bookmarks",
    "description": "Retrieves all active bookmarks for a user, including their related actions",
    "parameters": [
        OpenApiParameter(
            name="user_id",
            description="User ID to filter bookmarks by",
            required=True,
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
        200: BookmarkSerializer(many=True),
    },
    "examples": [
        OpenApiExample(
            "Success Response",
            value={
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
                "action_id": "123e4567-e89b-12d3-a456-426614174005"
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
    "summary": "Delete a bookmark",
    "description": "Performs a soft delete on a bookmark by changing its status to inactive",
    "parameters": [
        OpenApiParameter(
            name="id",
            description="Bookmark ID (UUID) to delete",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH
        ),
    ],
    "responses": {
        200: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    "examples": [
        OpenApiExample(
            "Success Response",
            value={
                "message": "Bookmark deleted successfully"
            },
            response_only=True,
        )
    ]
}

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
        200: BookmarkSerializer(many=True),
        400: OpenApiTypes.OBJECT,
    },
    "examples": [
        OpenApiExample(
            "Success Response",
            value={
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Example Bookmark",
                "url": "https://example.com",
                "client_id": "12345678",
                "status": True,
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
            },
            response_only=True,
        )
    ]
}
