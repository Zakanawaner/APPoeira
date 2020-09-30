import psycopg2
import json


class Database:
    def __init__(self):
        super(Database, self).__init__()
        self.groupsTableCreated = False
        self.eventsTableCreated = False
        self.onlineTableCreated = False
        self.rodaTableCreated = False
        self.connection = None
        self.cursor = None

    def check_tables(self):
        self.cursor.execute("SELECT * "
                            "FROM pg_catalog.pg_tables "
                            "WHERE schemaname != 'pg_catalog' "
                            "AND schemaname != 'information_schema';")
        tables = self.cursor.fetchall()
        for table in tables:
            if table[1] == 'groups': self.groupsTableCreated = True
            if table[1] == 'events': self.eventsTableCreated = True
            if table[1] == 'online': self.onlineTableCreated = True
            if table[1] == 'roda': self.rodaTableCreated = True

        if not self.groupsTableCreated:
            self.groupsTableCreated = True
            self.cursor.execute('CREATE TABLE groups ('
                                'fb_id text,'
                                'go_id text,'
                                'info json NOT NULL'
                                ');')
        if not self.eventsTableCreated:
            self.eventsTableCreated = True
            self.cursor.execute('CREATE TABLE events ('
                                'fb_id text,'
                                'go_id text,'
                                'info json NOT NULL'
                                ');')
        if not self.onlineTableCreated:
            self.onlineTableCreated = True
            self.cursor.execute('CREATE TABLE online ('
                                'fb_id text,'
                                'go_id text,'
                                'info json NOT NULL'
                                ');')
        if not self.rodaTableCreated:
            self.rodaTableCreated = True
            self.cursor.execute('CREATE TABLE roda ('
                                'fb_id text,'
                                'go_id text,'
                                'info json NOT NULL'
                                ');')
        self.connection.commit()
        self.cursor.execute("SELECT * "
                            "FROM pg_catalog.pg_tables "
                            "WHERE schemaname != 'pg_catalog' "
                            "AND schemaname != 'information_schema';")
        tables = self.cursor.fetchall()
        return tables

    def check_group(self, fb_id='', go_id=''):
        # False if the group is not in the DB, True otherwise
        self.open_connection()
        if go_id != '':
            self.cursor.execute("SELECT * FROM groups WHERE go_id = %s", (go_id,))
            if self.cursor.fetchone() is None: return False
        elif fb_id != '':
            self.cursor.execute("SELECT * FROM groups WHERE fb_id = %s", (fb_id,))
            if self.cursor.fetchone() is None: return False
        else:
            self.close_connection()
            return False
        self.close_connection()
        return True

    def insert_group(self, body, fb_id='', go_id=''):
        # Returns True if inserted (either new one or an id update)
        self.open_connection()
        done = False
        self.cursor.execute("SELECT * FROM groups")
        items = self.cursor.fetchall()
        if go_id != '':
            for item in items:
                if item[1] is None:
                    # En este if comparar que el nombre es o no es igual
                    if float('%.2f' % item[2]['location']['latitude']) == float('%.2f' % body['location']['latitude']) and float('%.2f' % item[2]['location']['longitude']) == float('%.2f' % body['location']['longitude']):
                        self.cursor.execute("UPDATE groups SET go_id = %s WHERE fb_id = {};", (go_id, item[2]['id']))
                        done = True
                        self.connection.commit()
            if not done:
                self.cursor.execute('INSERT INTO groups (go_id, info) VALUES (%s,%s)', (go_id, json.dumps(body)))
                done = True
                self.connection.commit()
        elif fb_id != '':
            for item in items:
                if item[0] is None:
                    # En este if comparar que el nombre es o no es igual
                    if float('%.2f' % item[2]['location']['latitude']) == float('%.2f' % body['location']['latitude']) and float('%.2f' % item[2]['location']['longitude']) == float('%.2f' % body['location']['longitude']):
                        self.cursor.execute("UPDATE groups SET fb_id = %s WHERE go_id = %s;", (fb_id, item[2]['id']))
                        done = True
                        self.connection.commit()
            if not done:
                self.cursor.execute('INSERT INTO groups (fb_id, info) VALUES (%s,%s)', (fb_id, json.dumps(body)))
                done = True
                self.connection.commit()
        else:
            done = False
        self.close_connection()
        return done

    def open_connection(self):
        self.connection = psycopg2.connect(user='Fernandez_Mario',
                                           password='vSythj02',
                                           host='127.0.0.1',
                                           port='5432',
                                           database='1000projects')
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()


# \c <database name>
# \dt -> shows all tables
# https://www.postgresqltutorial.com/postgresql-json/