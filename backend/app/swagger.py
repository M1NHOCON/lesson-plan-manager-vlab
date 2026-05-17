from flasgger import Swagger


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Lesson Plan Manager API",
        "description": "REST API for managing lesson plans.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "definitions": {
        "LessonPlanCreate": {
            "type": "object",
            "required": [
                "title",
                "objective",
                "summary",
                "planned_date",
                "discipline",
            ],
            "properties": {
                "title": {"type": "string", "example": "Introducao ao OSPF"},
                "objective": {"type": "string", "example": "Entender o OSPF"},
                "summary": {"type": "string", "example": "Aula introdutoria"},
                "planned_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2026-05-20",
                },
                "discipline": {"type": "string", "example": "Redes"},
                "contents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Conceitos", "Areas"],
                },
                "support_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Slides", "Laboratorio"],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["OSPF", "Redes"],
                },
            },
        },
        "LessonPlanUpdate": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "example": "OSPF basico"},
                "objective": {"type": "string", "example": "Revisar fundamentos"},
                "summary": {"type": "string", "example": "Atualizacao da aula"},
                "planned_date": {
                    "type": "string",
                    "format": "date",
                    "example": "2026-05-21",
                },
                "discipline": {"type": "string", "example": "Redes"},
                "contents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Roteamento dinamico"],
                },
                "support_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Simulador"],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["OSPF"],
                },
            },
        },
        "LessonPlan": {
            "allOf": [
                {"$ref": "#/definitions/LessonPlanCreate"},
                {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2026-05-17T18:53:20.919646",
                        },
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2026-05-17T18:53:20.919652",
                        },
                    },
                },
            ]
        },
        "Pagination": {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "example": 1},
                "per_page": {"type": "integer", "example": 10},
                "total_items": {"type": "integer", "example": 25},
                "total_pages": {"type": "integer", "example": 3},
                "has_next": {"type": "boolean", "example": True},
                "has_prev": {"type": "boolean", "example": False},
            },
        },
        "ValidationError": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Validation error"},
                "details": {"type": "array", "items": {"type": "object"}},
            },
        },
        "NotFoundError": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Lesson plan not found"},
            },
        },
        "AIRecommendationRequest": {
            "type": "object",
            "required": ["title", "discipline", "summary"],
            "properties": {
                "title": {
                    "type": "string",
                    "example": "Introducao ao OSPF",
                },
                "discipline": {
                    "type": "string",
                    "example": "Redes de Computadores",
                },
                "summary": {
                    "type": "string",
                    "example": "Aula introdutoria sobre roteamento dinamico usando OSPF.",
                },
            },
        },
        "AIRecommendationResponse": {
            "type": "object",
            "properties": {
                "contents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": [
                        "Conceito de roteamento dinamico",
                        "Funcionamento basico do OSPF",
                        "Areas OSPF",
                    ],
                },
                "related_topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": [
                        "Protocolos de roteamento",
                        "Topologias de rede",
                        "Convergencia de rede",
                    ],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["OSPF", "Redes", "Roteamento"],
                },
                "source": {
                    "type": "string",
                    "example": "mock",
                    "description": "Returned when fallback/mock recommendations are used.",
                },
            },
        },
    },
}


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}


def init_swagger(app):
    Swagger(app, template=swagger_template, config=swagger_config)
