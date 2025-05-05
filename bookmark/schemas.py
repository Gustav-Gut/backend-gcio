from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
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
                "count": 20,
                "next": "http://api.example.org/bookmarks/?page=2",
                "previous": None,
                "results": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Example Bookmark",
                        "url": "https://example.com",
                        "client_id": "12345678",
                        "actions": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174001",
                                "category": "Category",
                                "result": "Result",
                                "icon": "icon-name",
                                "color": "#FFF",
                                "sections": "section1,section2",
                                "status": True
                            }
                        ]
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
    "description": "Creates a new bookmark and returns its ID (UUID)",
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
                "client_id": "12345678",
                "external_source_id": "123e4567-e89b-12d3-a456-426614174002",
                "action_id": "123e4567-e89b-12d3-a456-426614174003",
                "status": True
            },
            request_only=True,
        ),
        OpenApiExample(
            "Success Response",
            value={
                "id": "123e4567-e89b-12d3-a456-426614174004"
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