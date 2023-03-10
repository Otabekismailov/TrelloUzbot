from database.trello import Database
from Keyboards.keyboards import get_inline_boards_btn, get_inline_lists_btn, get_members_btn, get_label_btn
from message import messages
import telebot
import os
from environs import Env
from telebot import custom_filters

from states.states import CreateNewTask, AddList
from Trello.trello import TrelloManager
from utils.utils import write_chat_to_csv, check_chat_id_from_csv, get_trello_username_by_chat_id, \
    get_member_tasks_message

env = Env()
env.read_env()

BOT_TOKEN = os.getenv("BOT_TOKEN")
state_storage = telebot.storage.StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage, parse_mode="html")


# /start
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, messages.WELCOME_MSG)


# /cancel
@bot.message_handler(commands=["cancel"])
def welcome(message):
    bot.send_message(message.chat.id, messages.CANCEL)


@bot.message_handler(commands=["register"])
def register_handler(message):
    if not check_chat_id_from_csv("chats.csv", message.chat.id):
        bot.send_message(message.chat.id, messages.SEND_TRELLO_USERNAME)
        bot.register_next_step_handler(message, get_trello_username)
    else:
        bot.send_message(message.chat.id, messages.ALREADY_REGISTERED)


# Trello username
def get_trello_username(message):
    write_chat_to_csv("chats.csv", message)
    bot.send_message(message.chat.id, messages.ADD_SUCCESSFULLY)


@bot.message_handler(commands=["boards"])
def get_boards(message):
    if not check_chat_id_from_csv("chats.csv", message.chat.id):
        bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)
    else:
        trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
        if trello_username:
            bot.send_message(
                message.chat.id, messages.SELECT_BOARD,
                reply_markup=get_inline_boards_btn(trello_username, "show_tasks")
            )
            Database(trello_username).user(message.chat.id, message.from_user.first_name,message.from_user.last_name)
        else:
            bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)


@bot.callback_query_handler(lambda c: c.data.startswith("show_tasks"))
def get_board_lists(call):
    message = call.message
    trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
    trello = TrelloManager(trello_username)
    board_id = call.data.split("_")[2]
    bot.send_message(
        message.chat.id, "Listni tanlang:", reply_markup=get_inline_lists_btn(trello, board_id, "show_list_tasks")
    )


@bot.callback_query_handler(lambda c: c.data.startswith("show_list_tasks_"))
def get_member_cards(call):
    message = call.message
    list_id = call.data.split("_")[3]
    trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
    trello = TrelloManager(trello_username)
    msg = Database(trello).cards_trello(list_id)
    if msg:
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, messages.NO_TASKS)


@bot.message_handler(commands=["new"])
def create_new_task(message):
    if not check_chat_id_from_csv("chats.csv", message.chat.id):
        bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)
    else:
        trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
        if trello_username:
            bot.send_message(
                message.chat.id, messages.CREATE_TASK,
                reply_markup=get_inline_boards_btn(trello_username, "new_tasks")
            )
            bot.set_state(message.from_user.id, CreateNewTask.board, message.chat.id)

        else:
            bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)


@bot.callback_query_handler(lambda call: call.data.startswith("new_tasks_"), state=CreateNewTask.board)
def get_new_task_name(call):
    message = call.message
    trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
    trello = TrelloManager(trello_username)
    board_id = call.data.split("_")[2]
    bot.send_message(
        message.chat.id, "Listni tanlang:", reply_markup=get_inline_lists_btn(trello, board_id, "new_doska")
    )
    bot.set_state(call.from_user.id, CreateNewTask.list, message.chat.id)
    with bot.retrieve_data(call.from_user.id, message.chat.id) as data:
        data["task_board_id"] = board_id


@bot.callback_query_handler(func=lambda call: call.data.startswith("new_doska"))
def get_list_id_for_new_task(call):
    message = call.message
    list_id = call.data.split("_")[2]
    bot.send_message(message.chat.id, messages.TASK_NAME)
    bot.set_state(call.from_user.id, CreateNewTask.name, message.chat.id)
    with bot.retrieve_data(call.from_user.id, message.chat.id) as data:
        data["task_list_id"] = list_id

    # bot.register_next_step_handler(message, get_task_name)


@bot.message_handler(state=CreateNewTask.name)
def get_task_name(message):
    bot.send_message(message.chat.id, messages.TASK_DESC)
    bot.set_state(message.from_user.id, CreateNewTask.description, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["task_name"] = message.text


@bot.message_handler(state=CreateNewTask.description)
def get_task_description(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["task_desc"] = message.text
        board_id = data["task_board_id"]
    trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)

    bot.send_message(
        message.chat.id,
        messages.TASK_MEMBERS,
        reply_markup=get_members_btn(trello_username=trello_username, board_id=board_id, action="new_task_member"))

    bot.set_state(message.from_user.id, CreateNewTask.members, message.chat.id)


@bot.callback_query_handler(lambda c: c.data.startswith("new_task_member"))
def get_member_id(call):
    message = call.message

    member_id = call.data.split("_")[3]

    with bot.retrieve_data(call.from_user.id, message.chat.id) as data:
        data["members_id"] = member_id
        board_id = data["task_board_id"]
    trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
    bot.send_message(message.chat.id, messages.TASK_LABELS,
                     reply_markup=get_label_btn(trello_username, board_id, "new_task_label"))
    bot.set_state(call.from_user.id, CreateNewTask.members, message.chat.id)


@bot.callback_query_handler(lambda c: c.data.startswith("new_task_label_"))
def get_label_id(call):
    message = call.message
    label_id = call.data.split("_")[3]
    bot.send_message(message.chat.id, messages.TASK_DEADLINE)
    bot.set_state(call.from_user.id, CreateNewTask.date, message.chat.id)
    with bot.retrieve_data(call.from_user.id, message.chat.id) as data:
        data["label_color"] = label_id
    bot.set_state(call.from_user.id, CreateNewTask.date, message.chat.id)
    bot.register_next_step_handler(message, get_data)


@bot.message_handler(states=CreateNewTask.date)
def get_data(message):
    bot.send_message(message.chat.id, messages.MESSAGE_INFO)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["task_data"] = message.text
        post = {
            "name": data["task_name"],
            "desc": data["task_desc"],
            "due": data["task_data"],
            "idList": data["task_list_id"],
            "idMembers": data["members_id"],
            "idLabels": data["label_color"],

        }
        trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
        TrelloManager(trello_username).post_data(data=post)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=["column"])
def get_boards(message):
    if not check_chat_id_from_csv("chats.csv", message.chat.id):
        bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)
    else:
        trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
        if trello_username:
            bot.send_message(
                message.chat.id, messages.SELECT_BOARD,
                reply_markup=get_inline_boards_btn(trello_username, "add_list")
            )
        else:
            bot.send_message(message.chat.id, messages.TRELLO_USERNAME_NOT_FOUND)


@bot.callback_query_handler(lambda call: call.data.startswith("add_list_"), state=AddList.board)
def get_new_task_name(call):
    message = call.message
    board_id = call.data.split("_")[2]

    bot.send_message(
        message.chat.id, messages.ADD_LIST)
    bot.set_state(call.from_user.id, AddList.name, message.chat.id)
    with bot.retrieve_data(call.from_user.id, message.chat.id) as data:
        data["board_id"] = board_id
    bot.register_next_step_handler(message, add_list)


@bot.message_handler(states=AddList.name)
def add_list(message):
    bot.send_message(
        message.chat.id, messages.MESSAGE_INFO)
    bot.set_state(message.from_user.id, AddList.name, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"] = message.text
        add = {
            "name": data["name"],
            "idBoard": data["board_id"]
        }
        trello_username = get_trello_username_by_chat_id("chats.csv", message.chat.id)
        TrelloManager(trello_username).list_add(list_aAd=add)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=["delete"])
def delete_card(message):
    bot.send_message(message.chat.id, "Ish jarayonida.......")


bot.add_custom_filter(custom_filters.StateFilter(bot))
my_commands = [
    telebot.types.BotCommand("/start", "Boshlash"),
    telebot.types.BotCommand("/register", "Ro'yxatdan o'tish"),
    telebot.types.BotCommand("/new", "Yangi task yaratish"),
    telebot.types.BotCommand("/boards", "Doskalarni ko'rish"),
    telebot.types.BotCommand("/column", "List Yaratish"),
    telebot.types.BotCommand("/delete", "O'chirish"),
    telebot.types.BotCommand("/cancel", "Bekor qilish"),
    telebot.types.BotCommand("/help", "Yordam")

]

if __name__ == "__main__":
    print("Started...")
    bot.set_my_commands(my_commands)
    bot.infinity_polling()
