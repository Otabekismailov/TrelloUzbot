# Users
ALL_USERS = "select * from users"
GET_USER_BY_CHAT_ID = "select * from users where chat_id = %s"
REGISTER_USER = """
    insert into
    users(chat_id, first_name, last_name, username)
    VALUES (%s, %s, %s, %s)
"""
UPDATE_USER_TRELLO_BY_CHAT_ID = """
    update users
    set trello_username = %s, trello_id = %s
    where chat_id = %s
"""
GET_USER_BY_TRELLO_ID = """
    select * from users where trello_id = %s
"""

# Boards
UPSERT_BOARDS = """
    insert into boards(name, trello_id)
    values (%s, %s)
    on conflict (trello_id)
    do update set name=excluded.name
"""
GET_BOARD_BY_TRELLO_ID = """
    select * from boards where trello_id = %s
"""

# Board Users
UPSERT_BOARD_USERS = """
    insert into boards_users(board_id, user_id)
    values (%s, %s)
    on conflict (board_id, user_id)
    do nothing
"""
GET_USER_BOARDS = """
    select b.name as name, b.trello_id as board_id from boards_users bu
    inner join boards b on bu.board_id = b.id
    where bu.user_id = %s
"""

# Lists
UPSERT_LISTS = """
    insert into lists(name, trello_id, board_id)
    values (%s, %s, %s)
    on conflict (trello_id)
    do update set name=excluded.name, board_id=excluded.board_id ,trello_id=excluded.trello_id
"""
GET_LIST_BY_TRELLO_ID = """
    select * from lists where trello_id=%s
"""
GET_LIST_BY_ID = """
    select lists.name,lists.trello_id  from lists 
    inner join boards b on lists.board_id = b.id
    where b.trello_id=%s
"""

# Cards
UPSERT_CARDS = """
    insert into cards(name, trello_id, url, description, list_id)
    values (%s, %s, %s, %s, %s)
    on conflict (trello_id)
    do update set name=excluded.name, url=excluded.url, description=excluded.description, list_id=excluded.list_id
"""
GET_CARD_ID_BY_TRELLO_ID = """
    select * from cards where trello_id = %s
"""

# Card members
GET_CARD_MEMBERS_BY_CARD_ID = """
    select * from cards_users where card_id = %s
"""
INSERT_CARD_MEMBER = """
    insert into cards_users(card_id, user_id) values (%s, %s)
"""
DELETE_CARD_MEMBER = """
    delete from cards_users where card_id = %s AND user_id = %s
"""
GET_USER_CARDS_BY_BOARD_ID = """
    select c.name as card_name, url from cards_users cu
    inner join cards c on c.id = cu.card_id
    inner join lists l on c.list_id = l.id
    inner join boards b on b.id = l.board_id
    where l.trello_id = %s and cu.user_id = %s
"""

UPSERT_MEMBERS = """
    insert into members(full_name, trello_username, trello_id)
    values (%s, %s, %s) on conflict (trello_id) do update set 
    full_name=excluded.full_name, trello_username=excluded.trello_username, trello_id=excluded.trello_id
"""

UPSERT_BOARD_MEMBERS_ID = """
    insert into boardsmembers as b(board_id, members_id)
    values (%s, %s) on conflict (board_id,members_id)do nothing 
   
"""

GET_MEMBER_BY_TRELLO_ID = """
select *
from members m
where m.trello_id =%s 
"""

GET_MEMBER_KEYBOARDS = """
select m.full_name,m.trello_id from members m
inner join boardsmembers b on m.id = b.members_id
inner join boards b2 on b.board_id = b2.id
where b2.trello_id=%s
"""

UPSERT_LABEL = """
insert into labels(name, color, trello_id, board_id) values (%s,%s,%s,%s) on conflict (trello_id) 
do update set name=excluded.name,color= excluded.color,trello_id= excluded.trello_id,board_id= excluded.board_id

"""

GET_LABEL_ID = """
select l.name,l.trello_id from labels l 
inner join boards b on l.board_id = b.id
where b.trello_id=%s
"""

SYNC_DOSTUP="""
select chat_id from users 
"""