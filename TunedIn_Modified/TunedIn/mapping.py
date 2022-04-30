map_body = {
    "properties": {
        "username": {
            "type": "keyword",
        },
        "password": {
            "type": "text"
        },
        "firstname": {
            "type": "text"
        },
        "lastname": {
            "type": "text"
        },
        "dob": {
            "type": "date",
            "format": "MM/dd/yyyy"
        },
        "contact": {
            "properties": {
                "email": {"type": "keyword"},
                "number": {"type": "long"}
            }
        },
        "skills": {
            "type": "text"
        },
        "yojtu": {
            "type": "integer"
        },
        "yoc": {
            "type": "integer"
        },
        "dept": {
            "type": "text"
        },
        "course": {
            "type": "text"
        },
        "currentsem": {
            "type": "integer"
        },
        "bio": {
            "type": "text"
        },
        "residence": {
            "type": "text"
        },
        "hostel": {
            "type": "text"
        },
        "education": {
            "type": "object",
            "enabled": "true"
        },
        "internships": {
            "type": "object"
        }

    }

}
