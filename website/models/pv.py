pv_validator = {
    "$jsonSchema": 
    {
        "bsonType": "object",
        "required": ["members"],
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
            }
        }
    }
}