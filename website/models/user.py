user_validator = {
    "$jsonSchema":
    {
        "bsonType": "object",
        "required": ["username", "password", "created_at"],
        "properties":
        {
            "username":
            {
                "bsonType": "string"
            },
            "password":
            {
                "bsonType": "binData"
            },
            "created_at":
            {
                "bsonType": "date"
            },
            "avatar":
            {
                "bsonType": "string"
            },
            "bio":
            {
                "bsonType": "string"
            },
            "groups":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "object",
                    "properties": {
                        "group":
                        {
                            "bsonType": "objectId"
                        },
                        "new_messages":
                        {
                            "bsonType": "int"
                        }
                    }
                }
            },
            "pvs":
            {
                "bsonType": "array",
                "items":
                {
                    "bsonType": "object",
                    "properties": {
                        "pv":
                        {
                            "bsonType": "objectId"
                        },
                        "new_messages":
                        {
                            "bsonType": "int"
                        }
                    }
                }
            },
            "last_online":
            {
                "bsonType": "date"
            },
            "sid":
            {
                "bsonType": "string"
            }
        }
    }
}
