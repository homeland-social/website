import os
import logging
import gevent
import socketio


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

AUTH = None
SIO = socketio.Server(async_mode='gevent')
USERS = {}


@SIO.event
def my_event(sid, message):
    SIO.emit('my_response', {'data': message['data']}, room=sid)


@SIO.event
def disconnect_request(sid):
    LOGGER.info('Websocket %s disconnecting', sid)
    SIO.disconnect(sid)


@SIO.event
def connect(sid, environ):
    # Kinda hacky, but I really want to reuse this auth backend.
    global AUTH

    LOGGER.info('Websocket %s connected', sid)

    from api.oauth import OAuth2Authentication
    if AUTH is None:
        AUTH = OAuth2Authentication()

    try:
        token = AUTH._authenticate(environ)

    except Exception as e:
        LOGGER.exception('Websocket %s authentication failed', sid)
        token = None

    if token is None:
        ConnectionRefusedError('Authentication failed')

    USERS[sid] = token


@SIO.event
def disconnect(sid):
    LOGGER.info('Websocket %s disconnected', sid)
    USERS.pop(sid, None)
