import re

from mysql.connector import MySQLConnection, Error

import enums
from mysql_dbconfig import read_db_config
import datetime
import base64
import json

dbconfig = read_db_config()
good_hours = 6


# кол-во часов актуальности данных в БД

def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row


def get_roles():
    try:
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM `roles`
            """)
        rows = cursor.fetchall()

        result = {
            "admin": [],
            "moder": []
        }

        for row in rows:
            result[row["type"]].append(row["user_id"])

        return result
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def add_query(user_id, query_type):
    try:

        conn = MySQLConnection(**dbconfig)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        INSERT INTO history(user_id, query_type, query_date) 
        VALUES(%(user_id)s, %(query_type)s, %(query_date)s)
        """, {
            'user_id': user_id,
            'query_type': query_type,
            'query_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        conn.commit()

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_group_data_users(group_id):
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT users FROM groups_users WHERE group_id = %(group_id)s AND updated >= %(updated)s
        """, {
            'group_id': group_id,
            'updated': (datetime.datetime.now() - datetime.timedelta(hours=good_hours)).strftime('%Y-%m-%d %H:%M:%S')
        })

        row = cursor.fetchone()

        if row is None:
            cursor.execute("""
            DELETE FROM groups_users WHERE group_id = %(group_id)s
            """, {
                'group_id': group_id
            })
            conn.commit()
            return 0
        else:
            return list(json.loads(base64.b64decode(row['users'])))

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def insert_group_data(group_id, group_data):
    try:

        conn = MySQLConnection(**dbconfig)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        INSERT INTO groups_users(group_id, users, updated) 
        VALUES(%(group_id)s, %(users)s, %(updated)s)
        """, {
            'group_id': group_id,
            'users': str(base64.b64encode(json.dumps(group_data).encode('ascii')), 'utf-8'),
            'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        conn.commit()

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_comments_data(group_id):
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)
        comments = {
            'listComments': [],
            'last_date': datetime.datetime.min
        }

        cursor.execute("""
                SELECT comment, comment_date FROM comments WHERE group_id = %(group_id)s 
                """, {
            'group_id': group_id
        })

        for row in iter_row(cursor, 50):
            if row['comment_date'] > comments['last_date']:
                comments['last_date'] = row['comment_date']
            comments['listComments'].append(row['comment'])

        return comments

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def insert_comments_data(group_id, comments):
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)
        last_comment_date = datetime.datetime.min

        for comment in comments:

            if comment['date'] > last_comment_date:
                last_comment_date = comment['date']

            if len(comment['text'].split()) < 3:
                continue

            cursor.execute("""
                    INSERT INTO comments(group_id, post_id, comment, comment_date) 
                    VALUES(%(group_id)s, %(post_id)s, %(comment)s, %(comment_date)s)
                    """, {
                'group_id': group_id,
                'post_id': comment['postId'],
                'comment': comment['text'],
                'comment_date': comment['date'],
            })

        cursor.execute("""
                    UPDATE groups_data SET last_comment_date = %(last_comment_date)s WHERE id = '%(group_id)s'
                """, {
            'last_comment_date': last_comment_date,
            'group_id': group_id
        })

        conn.commit()
        return cursor.rowcount

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def add_groups_to_history(user_id, groups_list):
    try:

        groups_list_str = ","
        groups_list_str = groups_list_str.join(groups_list)
        conn = MySQLConnection(**dbconfig)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        INSERT INTO groups_history(user_id, groups, added) 
        VALUES(%(user_id)s, %(groups)s, %(added)s)
        """, {
            'user_id': user_id,
            'groups': groups_list_str,
            'added': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        conn.commit()
        return cursor.lastrowid

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def set_groups_favorite(group_history_id):
    try:

        conn = MySQLConnection(**dbconfig)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            UPDATE groups_history SET favorite = '1' WHERE id = %(group_history_id)s
        """, {
            'group_history_id': group_history_id
        })
        conn.commit()

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row


def get_my_favorite(user_id):
    try:

        favorites = []
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM groups_history WHERE user_id = %(user_id)s AND favorite = '1' ORDER BY added DESC
        """, {
            'user_id': user_id
        })

        for row in iter_row(cursor, 50):
            favorites.append([row["id"], row["added"], row["groups"]])

        return favorites

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_favorite_groups(user_id, favoriteId):
    try:
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM groups_history WHERE id = %(favoriteId)s AND user_id = %(user_id)s
            """, {
            'favoriteId': favoriteId,
            'user_id': user_id
        })
        favoriteData = cursor.fetchone()

        if favoriteData is None:
            return 0
        else:
            return favoriteData["groups"]

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_history(user_id):
    result = []
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM history WHERE user_id = %(user_id)s ORDER BY query_date ASC", {
            'user_id': user_id
        })

        for row in iter_row(cursor, 50):
            result.append([row["query_date"], enums.HistoryText[row["query_type"]].value])

        return result

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_users(unique=False):
    result = []
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        query_placeholder = "user_id"
        if unique is not False:
            query_placeholder = "DISTINCT user_id"

        cursor.execute("""
        SELECT DATE(query_date) date, COUNT({}) counts 
        FROM history WHERE query_type = 'start' GROUP BY DATE(query_date)
        """.format(query_placeholder))

        for row in iter_row(cursor, 50):
            result.append({
                'date': row["date"],
                'counts': row["counts"]
            })

        return result

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_counts_of_using():
    result = []
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT DATE(query_date) date, COUNT(user_id) counts 
        FROM history WHERE query_type = 'start' GROUP BY DATE(query_date)
        """)

        for row in iter_row(cursor, 50):
            result.append({
                'date': row["date"],
                'counts': row["counts"]
            })

        return result

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def add_moder(admin_id):
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""INSERT IGNORE INTO roles
            SET user_id = %(user_id)s,
            type = 'moder'""",
                       {
                           'user_id': admin_id
                       })
        conn.commit()

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_group_data(group_domain):
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM groups_data WHERE group_domain = %(group_domain)s", {
            'group_domain': group_domain
        })

        row = cursor.fetchone()
        if row is not None:
            return row
        else:
            cursor.execute("""
                    INSERT INTO groups_data(group_domain) 
                    VALUES(%(group_domain)s)
                    """, {
                'group_domain': group_domain
            })
            conn.commit()
            return {
                'id': cursor.lastrowid,
                'last_comment_date': 0
            }

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_posts_comments_dates(group_id):
    result = {}
    try:

        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT post_id, MAX(comment_date) max_date FROM comments WHERE group_id = %(group_id)s GROUP BY post_id
        """, {
            'group_id': group_id
        })

        for row in iter_row(cursor, 50):
            result[row['post_id']] = row['max_date']

        return result

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    l = get_posts_comments_dates(1)
    print(l)
