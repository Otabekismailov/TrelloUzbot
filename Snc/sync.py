from psycopg2.extras import RealDictCursor
import query.quary
from database.trello import connection
from Trello.trello import TrelloManager


# Boards
def sync_boards(trello_username):
    trello = TrelloManager(trello_username)
    boards = trello.get_boards()
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        for board in boards:
            trello_board_id = board.get("id")
            cur.execute(query.quary.UPSERT_BOARDS, (board.get("name"), trello_board_id))
            connection.commit()
            cur.execute(query.quary.GET_BOARD_BY_TRELLO_ID, (trello_board_id,))
            db_board = cur.fetchone()  # from db
            sync_board_users(
                [member.get("idMember") for member in board.get("memberships")],
                db_board.get("id")
            )
            sync_lists(trello, trello_board_id, db_board.get("id"))


# Board users
def sync_board_users(board_member_ids, board_id):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        for member_id in board_member_ids:
            cur.execute(query.quary.GET_USER_BY_TRELLO_ID, (member_id,))
            user = cur.fetchone()
            if user:
                cur.execute(query.quary.UPSERT_BOARD_USERS, (board_id, user.get("id")))
                connection.commit()


# Lists on a board
def sync_lists(trello, trello_board_id, board_id):
    board_lists = trello.get_lists_on_a_board(trello_board_id)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        for board_list in board_lists:
            trello_list_id = board_list.get("id")
            cur.execute(
                query.quary.UPSERT_LISTS, (board_list.get("name"), board_list.get("id"), board_id)
            )
            connection.commit()
            cur.execute(query.quary.GET_LIST_BY_TRELLO_ID, (trello_list_id,))
            db_list = cur.fetchone()  # from db
            sync_cards(trello, trello_list_id, db_list.get("id"))


# Cards on a list
def sync_cards(trello, trello_list_id, list_id):
    list_cards = trello.get_cards_on_a_list(trello_list_id)
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        for card in list_cards:
            trello_card_id = card.get("id")
            cur.execute(
                query.quary.UPSERT_CARDS,
                (card.get("name"), trello_card_id, card.get("url"), card.get("desc"), list_id)
            )
            connection.commit()
            user_ids = []
            for member_id in card.get("idMembers"):
                cur.execute(query.quary.GET_USER_BY_TRELLO_ID, (member_id,))
                member = cur.fetchone()
                if member:
                    user_ids.append(member.get("id"))

            sync_card_members(trello_card_id, user_ids)


def sync_card_members(trello_card_id, user_ids):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query.quary.GET_CARD_ID_BY_TRELLO_ID, (trello_card_id,))
        card = cur.fetchone()
        card_id = card.get("id") if card else None
        cur.execute(query.quary.GET_CARD_MEMBERS_BY_CARD_ID, (card_id,))
        data = cur.fetchall()
        if not data:
            for user_id in user_ids:
                cur.execute(query.quary.INSERT_CARD_MEMBER, (card_id, user_id))
                connection.commit()


        else:
            existing_user_ids = [row.get("user_id") for row in data]
            must_remove_ids = list(set(existing_user_ids).difference(set(user_ids)))  # noqa
            for remove_id in must_remove_ids:
                cur.execute(query.quary.DELETE_CARD_MEMBER, (card_id, remove_id))
                connection.commit()
            must_add_ids = list(set(user_ids).difference(set(existing_user_ids)))
            for add_id in must_add_ids:
                cur.execute(query.quary.INSERT_CARD_MEMBER, (card_id, add_id))
                connection.commit()
        with connection.cursor(cursor_factory=RealDictCursor) as cur:
            # print(card.get('trello_id'))
            cur.execute(query.quary.GET_MEMBERS_ID, (card.get('trello_id'),))
            name = cur.fetchone()
            print(name.get('trello_id'))

    # def sync_member_list(member_id):
    #     # members = trello.get_board_members(member_id)
    #

    # trello_member = card.get("id")
    # cur.execute(
    #     query.quary.UPSERT_CARDS,
    #     (card.get("name"), trello_card_id, card.get("url"), card.get("desc"), list_id)
    # )
    # connection.commit()
    # user_ids = []
    # for member_id in card.get("idMembers"):
    #     cur.execute(query.quary.GET_USER_BY_TRELLO_ID, (member_id,))
    #     member = cur.fetchone()
    #     if member:
    #         user_ids.append(member.get("id"))
    # sync_card_members(trello_card_id, user_ids)
