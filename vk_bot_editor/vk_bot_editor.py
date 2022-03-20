import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_bot_editor import db_session
from random import choice

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


def parse_agrs(msg):
    msg = msg.split()
    return {'req': msg[0], 'args': msg[1:]}


def form_id(id):
    id = str(id)
    if '|' in id:
        id = id.split('|')[0][3:]
    return int(id)


class VkBotEditor:
    def __init__(self, token, group_id):
        print('Bot enabled')
        self.anss = []
        self.mesenges = None
        self.token = token
        self.group_id = group_id
        self.session = vk_api.VkApi(token=token)
        self.get_api = self.session.get_api()
        self.longpoll = VkBotLongPoll(self.session, str(group_id))

    def add_answer(self, req, function):
        self.anss.append((req, function))

    def start(self):
        print('Bot started')
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.message.text != '':
                    self.answer(event.message)

    def answer(self, message):
        self.mesenges = self.session.method('messages.getConversations',
                                            {'offset': 0, 'count': 20, 'filter': 'unanswered'})

        body = message.text
        if '|' in body and body.split('|')[0][1:] == 'club'+self.group_id:
            body = ' '.join(body.split()[1:])

        request = parse_agrs(body)
        for req, function in self.anss[::-1]:
            if request['req'].lower() == req:
                try:
                    function(self, message, *request['args'])
                    break
                except Exception:
                    pass

    def debug(self):
        print('Bot started in debug mode')
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.message.text != '':
                    self.debug_answer(event.message)

    def debug_answer(self, message):
        self.mesenges = self.session.method('messages.getConversations',
                                            {'offset': 0, 'count': 20, 'filter': 'unanswered'})
        body = message.text
        if '|' in body and body.split('|')[0][1:] == 'club'+self.group_id:
            body = ' '.join(body.split()[1:])

        request = parse_agrs(body)
        for req, function in self.anss[::-1]:
            if request['req'].lower() == req:
                function(self, message, *request['args'])
                break

    def send_message(self, to, text, keyboard=None):
        if keyboard is None:
            self.session.method('messages.send', {'peer_id': to, 'random_id': 0, 'message': text})
        else:
            self.session.method('messages.send', {'peer_id': to, 'random_id': 0, 'message': text,
                                                  'keyboard': open(keyboard, "r", encoding="UTF-8").read()})

    def kick(self, chat_id, user_id):
        self.get_api.messages.removeChatUser(chat_id=chat_id - 2000000000, user_id=user_id)


class VkBotEditorDB(VkBotEditor):
    def __init__(self, token, group_id, db_name):
        db_session.global_init(db_name)
        self.dbsession = db_session.create_session()
        super().__init__(token, group_id)

    def add(self, obj):
        self.dbsession.add(obj)
        self.dbsession.commit()

    def change(self, obj):
        self.dbsession.add(obj)
        self.dbsession.commit()

    def get_id(self, id, clas):
        object = self.dbsession.query(clas).filter(clas.id == id).all()
        if len(object) == 0:
            return None
        else:
            return object[0]

    def get_name(self, name, clas):
        object = self.dbsession.query(clas).filter(clas.name == name).all()
        if len(object) == 0:
            return None
        else:
            return object[0]

    def get_all(self, clas):
        return self.dbsession.query(clas).all()

    def get_random_id(self, id, clas):
        id = form_id(id)
        player1 = self.get_id(id, clas)
        users = sorted(self.get_all(clas), key=lambda x: abs(player1.level - x.level))
        for q in users:
            if q.id != player1.id and choice([0, 1]):
                return q
        for q in users:
            if q.id != player1.id:
                return q


VBEClass = (SqlAlchemyBase, SerializerMixin)


def column(clas, **args):
    clases = {'int': sqlalchemy.Integer,
              'str': sqlalchemy.String,
              'bool': sqlalchemy.Boolean,
              'datetime': sqlalchemy.DateTime,
              'date': sqlalchemy.Date
              }
    return sqlalchemy.Column(clases.get(clas), **args)


Column = column
