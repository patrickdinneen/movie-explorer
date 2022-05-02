from flask.wrappers import Request


def echo(event: Request):
    print(f'Processing {event} (type: {type(event)}')
    message = event.get_json()['message']
    message = message.upper()
    return message
