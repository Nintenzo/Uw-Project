def get_patch_data(payload):
    name = payload['name']
    avatar = payload['avatar']
    data = []
    for i, field in enumerate(payload['profile_fields']):
        try:
            field_data = field.get('community_member_profile_field', {})
            if i == 1:
                entry = {
                    "textarea": field_data.get("textarea", ""),
                    "profile_field_id": field['id'],
                    "id": field_data.get('id')
                }
            else:
                entry = {
                    "text": field_data.get("text", ""),
                    "profile_field_id": field['id'],
                    "id": field_data.get('id')
                }
        except Exception:
            entry = {
                "text": "",
                "profile_field_id": field.get('id'),
                "id": None
            }

        data.append(entry)

    payload_to_send = {
        "community_member":{
            "name": name,
            "avatar": avatar,
            "time_zone": "UTC",
            "locale": "en",
            "preferences": {
                "make_my_email_public": False,
                "messaging_enabled": True,
                "visible_in_member_directory": True
            },
            "community_member_profile_fields_attributes":data,  
        }
    }
        
    try:
        headline = payload['headline']
        payload_to_send['community_member']["headline"] = headline
    except Exception:
        pass
    return payload_to_send
