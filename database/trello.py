import environs
import psycopg2
import os
from psycopg2.extras import RealDictCursor
from Trello import trello
from Trello.trello import TrelloManager

env = environs.Env()
env.read_env()
connection = psycopg2.connect(
    dbname=os.getenv('NAMEDB'),
    user=os.getenv('USERDB'),
    password=os.getenv('PASSWORDDB'),
    host=os.getenv('hostdb'),
    port=5432
)
db = connection.cursor()
#
# class Database:
#     def __init__(self, trello_username):
#         self.trello_username = trello_username
#
#     def boards(self):
#         data = []
#         boards = TrelloManager(self.trello_username).get_boards()
#         for i in range(len(boards)):
#             curr = connection.cursor()
#             sql = f"insert into boards(board_name, trello_id, trello_username) values (%s,%s,%s) on conflict (trello_id)do update set board_name = EXCLUDED.board_name"
#             curr.execute(sql, (boards[i].get("name"), boards[i].get("id"), self.trello_username))
#             connection.commit()
#             curr.close()
#             with connection.cursor() as cur:
#                 cur.execute(
#                     f"select board_name,trello_id from boards where trello_id = '{boards[i]['id']}' or trello_username = '{self.trello_username}' ")
#                 s = cur.fetchall()
#                 for rows in s:
#                     data.append({'name': rows[0],
#                                  'id': rows[1]})
#         return data
#
#     def list_trello(self, board_id):
#         data = []
#         lists = trello.TrelloManager(self.trello_username).get_lists_on_a_board(board_id)
#         for i in range(len(lists)):
#             curr = connection.cursor()
#             sql = 'insert into lists(list_name, list_id,board_id,trello_boardid) values (%s,%s,%s,%s) on conflict (list_id) do update set list_name = EXCLUDED.list_name '
#             curr.execute(f"select id from boards where trello_id='{board_id}'")
#             name = curr.fetchall()
#             curr.execute(sql, (lists[i].get('name'), lists[i].get('id'), name[0][0], lists[i].get('idBoard')))
#             connection.commit()
#             curr.close()
#         with connection.cursor() as l:
#
#                 l.execute(
#                     f"select list_name,list_id from lists where trello_boardid = '{board_id}'or list_id='{lists[i]['id']}'")
#                 s = l.fetchall()
#                 for rows in s:
#                     data.append({'name': rows[0],
#                                  'id': rows[1]})
#         return data
#
#     def cards_trello(self, list_id):
#         card_data = trello.TrelloManager(self.trello_username).get_cards_on_a_list(list_id)
#         member_id = trello.TrelloManager(self.trello_username).get_member_id()
#         msg = ""
#         curr = connection.cursor()
#         for i in card_data:
#             if member_id in i.get("idMembers"):
#                 sql = 'insert into cards(cards_name,cards_id,des,url,list_id,cards_coid) values (%s,%s,%s,%s,%s,%s) ' \
#                       'on conflict (cards_id) do update set cards_name = EXCLUDED.cards_name'
#                 curr.execute(f"select id from lists  where list_id='{list_id}'")
#                 nama = curr.fetchall()
#                 curr.execute(sql,
#                              (i.get('name'), i.get('id'), i.get('desc'), i.get('url'), list_id, nama[0][0]))
#                 connection.commit()
#                 with connection.cursor() as cars:
#                     cars.execute(f"select cards_name from cards where cards_id='{i['id']}' or list_id='{list_id}'")
#                     name = cars.fetchall()
#                     for j in name:
#                         for g in j:
#                             msg += f"{i.get('idShort')} - {g}\n"
#         curr.close()
#         return msg
#
#     def members_label(self, board_id):
#         members = TrelloManager(self.trello_username).get_board_members(board_id)
#         data = []
#         for i in members:
#             curr = connection.cursor()
#             sql = 'insert into members(full_name,trello_username,trello_id)values (%s,%s,%s)' \
#                   'on conflict (trello_id) do update set full_name = excluded.full_name'
#             curr.execute(sql, (i.get('fullName'), i.get('username'), i.get('id')))
#             connection.commit()
#             with connection.cursor() as m:
#                 m.execute(f"select full_name,trello_id from members where trello_username ='{i['username']}'")
#                 s = m.fetchall()
#                 for row in s:
#                     data.append({
#                         'fullName': row[0],
#                         'id': row[1]
#                     })
#         con = connection.cursor()
#         sql = 'insert into members_one(cards_id)values (%s) on conflict (cards_id)do nothing '
#         con.execute('select id from cards')
#         name = con.fetchall()
#         for j in name:
#             con.execute(sql, (j))
#             connection.commit()
#         sql = 'insert into members_one(memberes_id)values (%s) on conflict (memberes_id)do update set memberes_id=excluded.memberes_id'
#         con.execute('select id from members')
#         name = con.fetchall()
#         for i in name:
#             con.execute(sql, (i))
#             connection.commit()
#         con.close()
#         return data
#
#     def labels_trello(self, board_id):
#         label = TrelloManager(self.trello_username).get_label(board_id)
#         data = []
#         for i in label:
#             curr = connection.cursor()
#             sql = 'insert into labels(label_name, color, label_id,board_id,board_d)values (%s,%s,%s,%s,%s)on conflict (label_id)do update set label_name = excluded.label_name'
#             curr.execute(f"select id from boards where trello_id='{board_id}'")
#             name = curr.fetchall()
#             curr.execute(sql, (i.get('name'), i.get('color'), i.get('id'), name[0][0], i.get('idBoard')))
#             connection.commit()
#             curr.close()
#         with connection.cursor() as l:
#             l.execute(f"select label_name,label_id from labels where board_d ='{board_id}'")
#             s = l.fetchall()
#             for i in s:
#                 data.append({
#                     'name': i[0],
#                     'id': i[1]
#
#                 })
#
#         con1 = connection.cursor()
#         card = 'insert into cards_label(card_id)values (%s) on conflict (card_id)do nothing '
#         con1.execute('select id from cards')
#         name = con1.fetchall()
#         for j in name:
#             con1.execute(card, (j))
#             connection.commit()
#         sql = 'insert into cards_label(label_id)values (%s) on conflict (label_id)do nothing '
#         con1.execute('select id from labels')
#         name = con1.fetchall()
#         for i in name:
#             con1.execute(sql, (i))
#             connection.commit()
#         con1.close()
#
#         return data

# def user(self, chat_id, full_name, last_name):
#     user = 'insert into users(chat_id,full_name,username,)values (%s,%s,%s,%s,%s) ' \
#            'on conflict (chat_id)do update set full_name=excluded.full_name'
#     cur.execute(f"select id from members where trello_username='{self.trello_username}'")
#     name = cur.fetchall()
#     for i in name:
#         cur.execute(user, (chat_id, full_name, self.trello_username, i, last_name))
#         connection.commit()
#     cur.close()

# card_data = Trello.trello.TrelloManager('otabekismailov3').get_cards_on_a_list('63ea22a4dd3aa382a077fba7')


# print(card_data)
# d = Database('otabekismailov3').labels_trello('64039b9d36372f1c57dcd97f')s
# s = Database('mrdeveloper10').list_trello('63ea22a4dd3aa382a077fb9f')
# print(s)
# '63ea22a4dd3aa382a077fb9f'
