import datetime

from vk_bot_editor.vk_bot_editor import VBEClass, Column


class User(*VBEClass):
    __tablename__ = 'users'

    id = Column('int', primary_key=True)
    name = Column('str')
    level = Column('int', default=1)
    atk = Column('int', default=0)
    df = Column('int', default=0)
    wins = Column('int', default=0)
    games = Column('int', default=0)
    winstreak = Column('int', default=0)
    upg = Column('int', default=0)
    created_date = Column('datetime', default=datetime.datetime.now)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f'{self.name} - {self.level} уровень, а\\з - {self.atk}\\{self.df}, ' \
               f'винрейт - {int(self.wins/self.games * 100 if self.games != 0 else 0)}%, ' \
               f'игр - {self.games}, серия - {self.winstreak}'
