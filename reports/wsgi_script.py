import io
from urllib.parse import parse_qs


# works for queries like this:
# curl 'http://localhost:8081/auth?user=obiwan&token=123'
# curl -X POST -d 'name=obiwan' -d 'email=linuxize@example.com' http://localhost:8081


def post_parser(father):
    local_list = []
    for key, value in father.items():
        if type(value) is dict:
            local_list.extend(post_parser(value))
        elif type(value) is list:
            values = ', '.join([val.decode('utf-8') for val in value])
            local_list.append(io.BytesIO((key.decode('utf-8') + ': ' + values + '\n').encode()).read())

    return local_list


def app(environ, start_response):
    response_data = []

    if environ['REQUEST_METHOD'] == "GET":
        data = environ['QUERY_STRING'].split('&')
        for single in data:
            result = ': '.join(single.split('=')) + '\n'
            response_data.append(io.BytesIO(result.encode()).read())
    elif environ['REQUEST_METHOD'] == "POST":
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0

        request_body = parse_qs(environ['wsgi.input'].read(request_body_size))
        response_data = post_parser(request_body)

    response_data_len = sum([len(s) for s in response_data])
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(response_data_len)),
    ]
    start_response(status, response_headers)
    return response_data
