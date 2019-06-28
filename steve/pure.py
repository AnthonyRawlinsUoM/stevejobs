#!/usr/bin/env python3
from pathlib import Path

import os
import socketio
import eventlet
import asyncio
import datetime as dt
import logging

from celery import Celery
from celery import group

from .celery_stalk import do_simulated_tasks
from .celery_stalk import do_revoke
from .celery_stalk import do_mp4


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("logger set to DEBUG")

sio = socketio.Server(async_mode='eventlet')

static_files = {'/': {'filename': 'index.html', 'content_type': 'text/html'},
                '/static/socket.io.js': 'static/socket.io.js',
                '/static/style.css': 'static/style.css',
                }
cel = Celery('facade',
             backend='redis://mq:6379/0',
             broker='redis://mq:6379/0')

app = socketio.WSGIApp(sio, static_files=static_files)

eventlet.monkey_patch(all=True)

with open(Path(os.getcwd()).joinpath('VERSION'), 'r') as vers:
    API_VERSION = vers.read()


@sio.event
def connect(sid, environ):
    print(">> I'm now connected.")
    print(sid)
    sio.emit(
        'welcome', {'data': {'message': 'Hello World! SID=%s, environ=%s' % (sid, environ)}}, room=sid)
    pass


@sio.event
def disconnect(data):
    print(">> I'm now disconnected.")
    pass


@sio.event
async def message(sid, data):
    with sio.session(sid) as session:
        print('>> Message from ', session['username'])
        print(data)


@sio.on('query')
def on_query(sid, data):
    print('>> I received a Query for JSON @ %s from %s' % (dt.datetime.now().isoformat(), sid))
    print(data)
    do_simulated_tasks(sid)
    pass


@sio.on('query mpg')
def on_mpg_query(sid, data):
    print('>> I received a Query for an MP4 @ %s from %s' % (dt.datetime.now().isoformat(), sid))
    print(data)

    final_result = group(
        [do_mp4.s(data['geo_json'], data['start'], data['finish'], model) for model in data['models']])

    res = final_result.delay()
    resulting_task_uuids = [
        {'uuid': r.id, 'api_version': API_VERSION} for r in res.children]

    return resulting_task_uuids


@sio.on('query nc')
def on_ncdf_query(sid, data):
    print('>> I received a Query for a NetCDF @ %s from %s' % (dt.datetime.now().isoformat(), sid))
    print(data)
    do_simulated_tasks(sid)
    pass


@sio.on('results')
def on_results(sid, data):
    print('>> Sending result @ %s to %s', (dt.datetime.now().isoformat()), sid)
    print(data)
    pass


@sio.on('revoke')
def on_revoke(sid, data):
    task_uuid = data['uuid']
    do_revoke(sid, task_uuid)
    pass


@sio.on('handshake')
def on_handshake(sid, data):
    print('>> I received a data from the client!')
    print(data)
    pass


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 3333)), app)
    cel.start()

    sio.emit('Server has awoken', {
             'data': 'A server is now available on *:3333'})
