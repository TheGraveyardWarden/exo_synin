message_validator = {
    "$jsonSchema": 
    {
        "bsonType": "object",
        "required": ["from", "text", "date"],
        "properties":
        {
            "from":
            {
                "bsonType": "objectId"
            },
            "text":
            {
                "bsonType": "string"
            },
            "date":
            {
                "bsonType": "date"
            },
            "file":
            {
                "bsonType": "string"
            }
        }
    }
}