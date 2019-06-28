import time
import socketio
from celery import Celery

cel = Celery('facade',
             backend='redis://mq:6379/0',
             broker='redis://mq:6379/0')


@cel.task(trail=True)
def do_simulated_tasks(sid):
    external_sio = socketio.RedisManager('redis://mq:6379/0', write_only=True)

    for i in range(10):
        external_sio.emit('results', data={'random_number': i}, room=sid)
        time.sleep(1)

    return 'Complete'


@cel.task(trail=True)
def do_revoke(sid, uuid):
    cel.control.revoke(uuid)
    external_sio = socketio.RedisManager('redis://mq:6379/0', write_only=True)
    external_sio.emit('celery task cancelled', data={'uuid': uuid}, room=sid)
    return 'Cancelled'


@cel.task(trail=True)
def do_mp4(sid, uuid):
    external_sio = socketio.RedisManager('redis://mq:6379/0', write_only=True)
    return 'Complete'