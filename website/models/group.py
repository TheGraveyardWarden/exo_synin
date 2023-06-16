group_validator = {
    "$jsonSchema":
    {
        "bsonType": "object",
        "required": ["name", "owner", "room", "is_channel", "description", "members"],
        "properties":
        {
            "members":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "objectId"
                }
            },
            "name":
            {
                "bsonType": "string"
            },
            "description":
            {
                "bsonType": "string"
            },
            "owner":
            {
                "bsonType": "objectId"
            },
            "room":
            {
                "bsonType": "objectId"
            },
            "messages":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "objectId"
                }
            },
            "pinned":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "objectId"
                }
            },
            "admins":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "objectId"
                }
            },
            "is_channel":
            {
                "bsonType": "bool"
            },
            "avatar":
            {
                "bsonType": "string"
            }
        }
    }
}