from psycopg2.extras import RealDictCursor

import database.trello
import query
from Trello import trello
from Trello.trello import TrelloManager
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from query.quary import GET_USER_BOARDS, GET_CARD_ID_BY_TRELLO_ID, GET_LIST_BY_TRELLO_ID, GET_LIST_BY_ID


def get_boards_btn(trello_username):
    boards_btn = ReplyKeyboardMarkup(resize_keyboard=True)
    boards = TrelloManager(trello_username).get_boards()
    if len(boards) % 2 == 0:
        last_board = None
    else:
        last_board = boards.pop()
    for board_index in range(len(boards) - 1):
        boards_btn.add(
            KeyboardButton(boards[board_index].get("name")),
            KeyboardButton(boards[board_index + 1].get("name"))
        )
    if last_board:
        boards_btn.add(KeyboardButton(last_board.get("name")))
    return boards_btn


def get_inline_boards_btn(user_id, action):
    inline_boards_btn = InlineKeyboardMarkup()
    with database.trello.connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(GET_USER_BOARDS, (user_id,))
        boards = cur.fetchall()
    if len(boards) % 2 == 0:
        last_board = None
    else:
        last_board = boards.pop()
    for board_index in range(0, len(boards) - 1, 2):
        inline_boards_btn.add(
            InlineKeyboardButton(
                boards[board_index].get("name"), callback_data=f'{action}_{boards[board_index].get("board_id")}'
            ),
            InlineKeyboardButton(
                boards[board_index + 1].get("name"), callback_data=f'{action}_{boards[board_index + 1].get("board_id")}'
            )
        )
    if last_board:
        inline_boards_btn.add(
            InlineKeyboardButton(last_board.get("name"), callback_data=f'{action}_{last_board.get("board_id")}')
        )
    return inline_boards_btn


def get_inline_lists_btn(board_id, action):
    lists_inline_btn = InlineKeyboardMarkup()
    with database.trello.connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(GET_LIST_BY_ID, (board_id))
        lists = cur.fetchall()
    if len(lists) % 2 == 0:
        last_list = None
    else:
        last_list = lists.pop()
    for list_index in range(0, len(lists) - 1, 2):
        lists_inline_btn.add(
            InlineKeyboardButton(
                lists[list_index].get("name"),
                callback_data=f'{action}_{lists[list_index].get("id")}'
            ),
            InlineKeyboardButton(
                lists[list_index + 1].get("name"),
                callback_data=f'{action}_{lists[list_index + 1].get("id")}'
            ),
        )
    if last_list:
        lists_inline_btn.add(
            InlineKeyboardButton(
                last_list.get("name"), callback_data=f'{action}_{last_list.get("id")}'
            )
        )
    return lists_inline_btn


def get_members_btn(trello_username, board_id, action):
    # members = TrelloManager(trello_username).get_board_members(board_id)
    members =141
    members_btn = InlineKeyboardMarkup()
    if len(members) == 1:
        for i in range(len(members)):
            members_btn.add(
                InlineKeyboardButton(
                    members[i].get("fullName"),
                    callback_data=f'{action}_{members[i].get("id")}'
                ))
    else:
        if len(members) % 2 == 0:

            last_member = None
        else:
            last_member = members.pop()
        for i in range(0, len(members) - 1, 2):
            members_btn.add(
                InlineKeyboardButton(
                    members[i].get("fullName"),
                    callback_data=f'{action}_{members[i].get("id")}'
                ),
                InlineKeyboardButton(
                    members[i + 1].get("fullName"),
                    callback_data=f'{action}_{members[i + 1].get("id")}'
                ),
            )
        if last_member:
            members_btn.add(
                InlineKeyboardButton(
                    last_member.get("name"), callback_data=f'{action}_{last_member.get("id")}'
                )
            )
    return members_btn


def get_label_btn(trello_username, board_id, action):
    # label = TrelloManager(trello_username).get_label(board_id)
    label = database.trello.Database(trello_username).labels_trello(board_id)
    lebel_btn = InlineKeyboardMarkup()
    if len(label) % 2 == 0:
        last_label = None
    else:
        last_label = label.pop()
    for i in range(0, len(label) - 1, 2):
        lebel_btn.add(
            InlineKeyboardButton(
                label[i].get("name"),
                callback_data=f'{action}_{label[i].get("id")}'
            ),
            InlineKeyboardButton(
                label[i + 1].get("name"),
                callback_data=f'{action}_{label[i + 1].get("id")}'
            ),
        )
    if last_label:
        lebel_btn.add(
            InlineKeyboardButton(
                last_label.get("name"), callback_data=f'{action}_{last_label.get("id")}'
            )
        )

    return lebel_btn
# s = get_label_btn('otabekismailov3', '64039b9d36372f1c57dcd97f', 'dsds')
# print(s)
