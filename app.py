from asyncio import coroutine, get_event_loop
from sys import stderr
from json import dumps
from os import environ

from aiohttp.web import Application
from aiohttp_jinja2 import setup as jinja2_setup, template, render_template
from jinja2 import FileSystemLoader
from aiohttp.web import Response

@coroutine
def get_name(request):
    context = {'name': request.match_info.get('name', 'Anonymous')}
    response = render_template('name.jinja2', request, context)
    return response

@coroutine
def post_name(request):
    print(request.headers)
    if request.headers.get('CONTENT-TYPE') == 'application/json':
        body = yield from request.json()
        data = request.headers.get('CONTENT-TYPE')
    else:
        body = yield from request.post()
        data = request.headers.get('CONTENT-TYPE')
    body = dumps(dict(body))
    resp = 'CONTENT-TYPE {0}\n\nYour request\n\n\n {1}'.format(data, body)
    return Response(body=resp.encode())

@coroutine
def init(loop):
    app = Application(loop=loop)
    jinja2_setup(app, loader=FileSystemLoader('templates'))

    app.router.add_route('GET', '/name/{name}', get_name)
    app.router.add_route('POST', '/post', post_name)

    host = '0.0.0.0'
    port = environ.get('PORT', 8000)
    srv = yield from loop.create_server(app.make_handler(), host, port)
    print('Server started at http://{0}:{1}'.format(host, port))
    return srv

loop = get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Interrupted', file=stderr)
