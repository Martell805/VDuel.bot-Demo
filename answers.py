from random import randint, uniform
from classes import User
from vk_bot_editor.vk_bot_editor import *


def test(session, message):
    session.send_message(message.peer_id, '4321')


def echo(session, message, *msg):
    session.send_message(message.peer_id, ' '.join(msg))


def register(session, message, name):
    user = session.get_id(message.from_id, User)
    if user:
        session.send_message(message.peer_id, f'[id{user.id}|{user.name}], вы уже зарегистрированы, ваш id - {user.id}'
                                              f', а уровень - {user.level}')
        return

    if name.lower() == 'random':
        session.send_message(message.peer_id, f'Недопустимое имя!')
        return

    user = User(message.from_id, name)
    session.add(user)
    session.send_message(message.peer_id, f'[id{user.id}|{user.name}], вы успешно зарегистрированы,'
                                          f' ваш id - {user.id}, а уровень - {user.level}')


def help(session, message):
    msg = """
    Список команд:
    1. "register <имя(без пробелов)>" - зарегистрироваться на имя <имя>
    2. "duel <пользователь>" - дуэль с <пользователь>. Если написать <пользователь> = "random"  - запустится дуэль 
    со случайным игроком
    3."duel_to_dead <пользователь>" - дуэль насмерть с <пользователь> (может проходить только в беседе,
     где есть оба пользователя)
    4. "info <пользователь>" - вся информация о <пользователе>, если оставить пустым - о вас
    5. "top <n=10>" - выводит <n> пользователей с самым высоким уровнем
    6. "send <пользователь> <n>" - отправить <n> очков улучшения <пользователю>
    7. "upgrade" - показывает информацию об возможных улучшениях
    8. "1234" - бот ответит "4321"
    9. "echo <сообщение>" - бот скажет <сообщение>
    10. "help" - список команд
    """
    session.send_message(message.peer_id, msg, 'keyboards/keyboard.json')


def info(session, message, *args):
    user1 = session.get_id(form_id(message.from_id), User)
    if args:
        id = args[0]
        if '|' not in str(id) and not str(id).isdigit():
            user = session.get_name(str(id), User)
            id = user.id
        else:
            user = session.get_id(form_id(id), User)
    else:
        id = form_id(message.from_id)
        user = session.get_id(form_id(message.from_id), User)

    if not user or id <= 100:
        if args:
            session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], тот, о ком вы просите информацию, '
                                                  f'не зарегистрирован. Для регистрации напишите "register <имя>"')
        else:
            session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')
        return

    msg = f"""{user.name}:
    id      - {user.id}
    Уровень - {user.level}
    Атака   - {user.atk}
    Защита  - {user.df}
    Игр     - {user.games}
    Винрейт - {user.wins/user.games * 100 if user.games != 0 else 0}%
    Серия   - {user.winstreak}
    """
    session.send_message(message.peer_id, msg)


def choose_winner(player1, player2):
    winner = choice([1] * min(player1.level, player2.level * 2) + [2] * min(player2.level, player1.level * 2))
    return winner


def choose_winner_2ad(player1, player2):
    winner = choice([1] * max((player1.atk - player2.df), 1) + [2] * max((player2.atk - player1.df), 1))
    return winner


def choose_winner_3o(player1, player2):
    p1 = min(max((player1.atk - player2.df), 1), 4)
    p2 = min(max((player2.atk - player1.df), 1), 4)
    winner = randint(0, p1 + p2)
    if winner < p1:
        return 1, p1/(p1 + p2)
    else:
        return 2, p2/(p1 + p2)


def choose_winner_4u(player1, player2):
    p1 = min(max((player1.atk/max(1, player2.df)), 1), 4)
    p2 = min(max((player2.atk/max(1, player1.df)), 1), 4)
    winner = uniform(0, p1 + p2)
    if winner < p1:
        return 1, p1/(p1 + p2)
    else:
        return 2, p2/(p1 + p2)


def get_reward(player1, player2):
    return max(1, min(int(player2.level/player1.level), 50)), max(1, min(int(player1.level/player2.level), 50))


def duel(session, message, id):
    player1 = session.get_id(form_id(message.from_id), User)
    if not player1:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')
        return

    if id != 'random':
        if '|' not in str(id) and not str(id).isdigit():
            player2 = session.get_name(str(id), User)
        else:
            player2 = session.get_id(form_id(id), User)
    else:
        player2 = session.get_random_id(message.from_id, User)

    if not player2 or (id != 'random' and player2.id <= 100):
        session.send_message(message.peer_id, f'[id{player1.id}|{player1.name}], nот, кого вы вызываете на дуэль, '
                                              f'не зарегистрирован. Для регистрации напишите "register <имя>"')
        return

    if player1.id == player2.id:
        session.send_message(message.peer_id, f'{player1.name}, нельзя запускать дуэль с самим собой!')
        return

    # -------------------------------------------------------------------------------------------------------- #
    winner = choose_winner_4u(player1, player2)
    if winner[0] == 1:
        player1.winstreak += 1
        player2.winstreak = 0
        player1.level += player1.winstreak
        player2.level = max(1, player2.level - 1)
        player1.upg += player1.winstreak
        player1.games += 1
        player1.wins += 1
        player2.games += 1
        session.change(player1)
        session.change(player2)
        session.send_message(message.peer_id, f'[id{player1.id}|{player1.name}] победил '
                                              f'[id{player2.id}|{player2.name}] с шансом '
                                              f'{int(winner[1] * 100)}%! '
                                              f'Уровень выигравшего повышается на {player1.winstreak} '
                                              f'и становится {player1.level}! '
                                              f'Теперь его серия побед {player1.winstreak}!')
        try:
            session.send_message(player2.id, f'[id{player1.id}|{player1.name}] вызвал вас на дуэль '
                                             f'и победил с шансом {int(winner[1] * 100)}%! '
                                             f'Его уровень повышается на {player1.winstreak} '
                                             f'и становится {player1.level}! '
                                             f'Теперь его серия побед {player1.winstreak}!')
        except Exception:
            pass
    else:
        player1.level = max(1, player1.level - 1)
        player2.winstreak += 1
        player1.winstreak = 0
        player2.level += player2.winstreak
        player2.upg += player2.winstreak
        player1.games += 1
        player2.wins += 1
        player2.games += 1
        session.change(player1)
        session.change(player2)
        session.send_message(message.peer_id, f'[id{player2.id}|{player2.name}] победил '
                                              f'[id{player1.id}|{player1.name}] с шансом '
                                              f'{int(winner[1] * 100)}%!'
                                              f' Уровень выигравшего повышается на {player2.winstreak} '
                                              f'и становится {player2.level}! '
                                              f'Теперь его серия побед {player2.winstreak}!')
        try:
            session.send_message(player2.id, f'[id{player1.id}|{player1.name}] вызвал вас на дуэль и '
                                             f'вы победили с шансом {int(winner[1] * 100)}%! '
                                             f'Ваш уровень повышается на {player2.winstreak}'
                                             f' и становится {player2.level}! '
                                             f'Теперь ваша серия побед {player2.winstreak}!')
        except Exception:
            pass
    # -------------------------------------------------------------------------------------------------------- #


def top(session, message, *n):
    if n:
        n = int(n[0])
    else:
        n = 10
    users = sorted(filter(lambda x: x.id > 100, session.get_all(User)), key=lambda x: -x.level)
    msg = ''
    for q in range(min(n, len(users))):
        msg += f'{q + 1}. {users[q]}\n'
    session.send_message(message.peer_id, msg)


def upgrade(session, message):
    user = session.get_id(form_id(message.from_id), User)
    if user:
        msg = f"""
[id{user.id}|{user.name}], у вас есть {user.upg} свободных очков
Вы можете улучшить защиту на <n> очков, 
написав "upgrade_def <n>", или атаку, написав "upgrade_atk <n>"
Атака и защита в равной степени влияют на шанс победы
        """
        session.send_message(message.peer_id, msg, 'keyboards/upgrade.json')
    else:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')


def upgrade_def(session, message, n):
    user = session.get_id(form_id(message.from_id), User)
    if user:
        n = int(n)
        if user.upg >= n:
            user.df += n
            user.upg -= n
            session.send_message(message.peer_id, f'[id{user.id}|{user.name}], ваша защита повышена на {n} '
                                                  f'и теперь составляет {user.df}. Для '
                                                  f'получения большего количества участвуйте в дуэлях! Сейчас у вас'
                                                  f' {user.upg} свободных очков')
            session.change(user)
        else:
            session.send_message(message.peer_id, f'[id{user.id}|{user.name}], вам не хватает очков '
                                                  f'для повышения защиты. Для '
                                                  f'получения большего количества участвуйте в дуэлях! Сейчас у вас'
                                                  f' {user.upg} свободных очков')
    else:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')


def upgrade_atk(session, message, n):
    user = session.get_id(form_id(message.from_id), User)
    if user:
        n = int(n)
        if user.upg >= n:
            user.atk += n
            user.upg -= n
            session.send_message(message.peer_id, f'[id{user.id}|{user.name}], ваша атака повышена на {n} '
                                                  f'и теперь составляет {user.atk}. Для '
                                                  f'получения большего количества участвуйте в дуэлях! Сейчас у вас'
                                                  f' {user.upg} свободных очков')
            session.change(user)
        else:
            session.send_message(message.peer_id, f'[id{user.id}|{user.name}], вам не хватает очков '
                                                  f'для повышения атаки. Для получения большего количества '
                                                  f'участвуйте в дуэлях! Сейчас у вас'
                                                  f' {user.upg} свободных очков')
    else:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')


def add_bots(session, n, max_lvl):
    for q in range(0, n):
        id_b = q
        bot = User(id_b, f'Bot#{id_b}')
        bot.level = randint(1, max_lvl)
        bot.df = randint(0, bot.level)
        bot.atk = bot.level - bot.df
        session.add(bot)


def send(session, message, id, n):
    n = int(n)
    user1 = session.get_id(form_id(message.from_id), User)
    if not user1:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')
        return
    if '|' not in str(id) and not str(id).isdigit():
        user2 = session.get_name(str(id), User)
    else:
        user2 = session.get_id(form_id(id), User)
    if not user2:
        session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], тот, кому вы собираетесь отправить '
                                              f'очки улучшения, не зарегистрирован. '
                                              f'Для регистрации напишите "register <имя>"')
        return
    if n > user1.upg:
        session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], вам не хватает очков '
                                              f'для отправки {user2.name}. Для получения большего '
                                              f'количества участвуйте в дуэлях!')
        return

    if n < 0:
        session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], '
                                              f'нельзя отправлять отрицательное количество очков')
        return

    user1.upg -= n
    user2.upg += n
    session.change(user1)
    session.change(user2)

    session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], вы успешно отправили {n} очков '
                                          f'{user2.name}. Для получения большего количества участвуйте в дуэлях!')

    try:
        session.send_message(user2.id, f'[id{user2.id}|{user2.name}], [id{user1.id}|{user1.name}] отправил вам {n} '
                                       f'очков. Для получения большего количества участвуйте в дуэлях!')
    except Exception:
        pass


def kick(session, message, id):
    user1 = session.get_id(form_id(message.from_id), User)
    if not user1:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')
        return
    if '|' not in str(id) and not str(id).isdigit():
        user2 = session.get_name(str(id), User)
    else:
        user2 = session.get_id(form_id(id), User)
    if not user2:
        session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}], тот, кого вы собираетесь кикнуть '
                                              f'не зарегистрирован. Для регистрации напишите "register <имя>"')
        return

    session.send_message(message.peer_id, f'[id{user1.id}|{user1.name}] кикнул [id{user2.id}|{user2.name}]'
                                          f' из {message.peer_id}')
    print(message.chat_id)
    session.kick(message.peer_id, user2.id)


def chat_info(session, message):
    print(session.get_api.method("messages.getChat", {"peer_id": message.peer_id - 2000000000}))


def duel_to_dead(session, message, id):
    player1 = session.get_id(form_id(message.from_id), User)
    if not player1:
        session.send_message(message.peer_id, f'Вы не зарегистрированны, для регистрации напишите "register <имя>"')
        return

    if '|' not in str(id) and not str(id).isdigit():
        player2 = session.get_name(str(id), User)
    else:
        player2 = session.get_id(form_id(id), User)

    if not player2 or player2.id <= 100:
        session.send_message(message.peer_id, f'[id{player1.id}|{player1.name}], тот, кого вы вызываете на дуэль, '
                                              f'не зарегистрирован. Для регистрации напишите "register <имя>"')
        return

    if player1.id == player2.id:
        session.send_message(message.peer_id, f'{player1.name}, нельзя запускать дуэль с самим собой!')
        return

    if message.peer_id <= 2000000000:
        session.send_message(message.peer_id, f'{player1.name}, дуэль насмерть можно запускато только в беседе!')

    # -------------------------------------------------------------------------------------------------------- #
    winner = choose_winner_4u(player1, player2)
    if winner[0] == 1:
        player1.winstreak += 1
        player2.winstreak = 0
        player1.level += player1.winstreak
        player2.level = max(1, player2.level - 1)
        player1.upg += player1.winstreak
        player1.games += 1
        player1.wins += 1
        player2.games += 1
        session.change(player1)
        session.change(player2)
        session.send_message(message.peer_id, f'[id{player1.id}|{player1.name}] победил '
                                              f'[id{player2.id}|{player2.name}] с шансом '
                                              f'{int(winner[1] * 100)}%!\n'
                                              f'Уровень выигравшего повышается на {player1.winstreak} '
                                              f'и становится {player1.level}\n'
                                              f'Теперь его серия побед {player1.winstreak}\n'
                                              f'[id{player2.id}|{player2.name}] погибает и вылетает из беседы!')
        session.kick(message.peer_id, player2.id)
        try:
            session.send_message(player2.id, f'[id{player1.id}|{player1.name}] вызвал вас на дуэль '
                                             f'и победил с шансом {int(winner[1] * 100)}%!\n'
                                             f'Вы были кикнуты из беседы, в которой прошла дуэль')
        except Exception:
            pass
    else:
        player1.level = max(1, player1.level - 1)
        player2.winstreak += 1
        player1.winstreak = 0
        player2.level += player2.winstreak
        player2.upg += player2.winstreak
        player1.games += 1
        player2.wins += 1
        player2.games += 1
        session.change(player1)
        session.change(player2)
        session.send_message(message.peer_id, f'[id{player2.id}|{player2.name}] победил '
                                              f'[id{player1.id}|{player1.name}] с шансом '
                                              f'{int(winner[1] * 100)}%!'
                                              f' Уровень выигравшего повышается на {player2.winstreak} '
                                              f'и становится {player2.level}\n'
                                              f'Теперь его серия побед {player2.winstreak}\n'
                                              f'[id{player1.id}|{player1.name}] погибает и вылетает из беседы!')
        session.kick(message.peer_id, player1.id)
        try:
            session.send_message(player2.id, f'[id{player1.id}|{player1.name}] вызвал вас на дуэль и '
                                             f'вы победили с шансом {int(winner[1] * 100)}%!\n'
                                             f'Ваш уровень повышается на {player2.winstreak} '
                                             f'и становится {player2.level}\n'
                                             f'Теперь ваша серия побед {player2.winstreak}\n'
                                             f'[id{player1.id}|{player1.name}] был кикнуты из беседы, '
                                             f'в которой прошла дуэль')
        except Exception:
            pass
    # -------------------------------------------------------------------------------------------------------- #
