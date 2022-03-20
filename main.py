from vk_bot_editor.vk_bot_editor import VkBotEditorDB
import answers


session = VkBotEditorDB('SECRET_TOKEN',
                        'GROUP_ID', 'db/DuB.sqlite')

session.add_answer('1234', answers.test)
session.add_answer('echo', answers.echo)
session.add_answer('register', answers.register)
session.add_answer('duel', answers.duel)
session.add_answer('help', answers.help)
session.add_answer('start', answers.help)
session.add_answer('начать', answers.help)
session.add_answer('info', answers.info)
session.add_answer('top', answers.top)
session.add_answer('upgrade', answers.upgrade)
session.add_answer('upgrade_atk', answers.upgrade_atk)
session.add_answer('upgrade_def', answers.upgrade_def)
session.add_answer('send', answers.send)
session.add_answer('duel_to_dead', answers.duel_to_dead)
# session.add_answer('kick', answers.kick)
# session.add_answer('chat_info', answers.chat_info)

session.start()
