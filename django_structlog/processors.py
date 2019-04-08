import uuid


def add_id(logger, log_method, event_dict):
    event_dict["id"] = str(uuid.uuid4())
    return event_dict


def add_request_id(logger, log_method, event_dict):
    event_dict["request_id"] = event_dict['_record'].request_id
    return event_dict
