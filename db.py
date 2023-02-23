import sqlite3
from sqlite3 import Error
from json import load


class DB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.create_db_connection()
        self.create_tables()
        sql_skills_query = '''SELECT json_group_array(json_object(
            \'skill\', skill,
            \'rating\', rating))
            FROM skill_hacker_join WHERE hacker_id=id'''
        self.sql_hackers_query = f'''SELECT json_group_array(json_object(
            \'id\', id,
            \'name\', name,
            \'company\', company,
            \'email\', email,
            \'phone\', phone,
            \'registered\', registered,
            \'skills\', ({sql_skills_query})))
            FROM hackers'''
        sql_attendees_query = '''SELECT json_group_array(json_object(
            \'name\', (SELECT name from hackers WHERE id=hacker_id)))
            FROM event_hacker_join WHERE event_id=id'''
        self.sql_events_query = f'''SELECT json_group_array(json_object(
            \'id\', id,
            \'title\', title,
            \'time\', time,
            \'place\', place,
            \'attendees\', ({sql_attendees_query})))
            FROM events'''

    def create_db_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.execute('PRAGMA foreign_keys = ON')
        except Error as e:
            print(e)

    def create_tables(self):
        sql_hackers_table = """ CREATE TABLE IF NOT EXISTS hackers (
                                            id integer,
                                            name text NOT NULL,
                                            company text NOT NULL,
                                            email text NOT NULL,
                                            phone text NOT NULL,
                                            registered text NOT NULL,
                                            PRIMARY KEY (id),
                                            UNIQUE(name)
                                        ); """
        sql_skills_table = """ CREATE TABLE IF NOT EXISTS skills (
                                            name text NOT NULL,
                                            PRIMARY KEY (name),
                                            UNIQUE(name)
                                        ); """
        skill_hacker_join_table = """ CREATE TABLE IF NOT EXISTS skill_hacker_join (
                                            hacker_id integer NOT NULL,
                                            skill text NOT NULL,
                                            rating integer NOT NULL,
                                            FOREIGN KEY(hacker_id) REFERENCES hackers (id),
                                            FOREIGN KEY(skill) REFERENCES skills (name)
                                            UNIQUE(hacker_id, skill)
                                        ); """
        sql_events_table = """ CREATE TABLE IF NOT EXISTS events (
                                            id integer,
                                            title text NOT NULL,
                                            time text NOT NULL,
                                            place text NOT NULL,
                                            PRIMARY KEY (id),
                                            UNIQUE(title)
                                        ); """
        event_hacker_join_table = """ CREATE TABLE IF NOT EXISTS event_hacker_join (
                                            hacker_id integer NOT NULL,
                                            event_id integer NOT NULL,
                                            FOREIGN KEY(hacker_id) REFERENCES hackers (id),
                                            FOREIGN KEY(event_id) REFERENCES events (id),
                                            UNIQUE(hacker_id, event_id)
                                        ); """
        cursor = self.conn.cursor()
        for query in [sql_hackers_table, sql_skills_table, skill_hacker_join_table, sql_events_table, event_hacker_join_table]:
            cursor.execute(query)

    def populate_db(self):
        # Load Hacker Data
        data = load(open("HTN_2023_BE_Challenge_Data.json"))
        cursor = self.conn.cursor()
        for hacker in data:

            # Create hacker row
            attributes = [str(hacker[item]) for item in ('name', 'company', 'email', 'phone')]
            attributes.append('false')
            sql_hacker_row = ''' INSERT OR IGNORE INTO hackers(name,company,email,phone,registered)
                    VALUES(?,?,?,?,?) '''
            cursor.execute(sql_hacker_row, attributes)

            # Create skill row
            for skill in hacker['skills']:
                sql_skill_row = ''' INSERT OR IGNORE INTO skills(name)
                        VALUES(?)'''
                cursor.execute(sql_skill_row, [skill['skill']])
            
            # Create skill_hacker_join row
            sql = f'SELECT id FROM hackers WHERE name = \'{hacker["name"]}\''
            hacker_id = cursor.execute(sql).fetchone()[0]
            sql = "INSERT OR IGNORE INTO skill_hacker_join(hacker_id,skill,rating) VALUES(?,?,?)"
            for skill in hacker['skills']:
                cursor.execute(sql, (hacker_id, skill['skill'], skill['rating']))

        # Load Event Data  
        event_data = load(open("HTN_2023_event_data.json"))
        for event in event_data:

            # Create event row
            attributes = [str(event[item]) for item in ('title', 'time', 'place')]
            sql_event_row = 'INSERT OR IGNORE INTO events(title,time,place) VALUES(?,?,?)'
            cursor.execute(sql_event_row, attributes)

        self.conn.commit()
    
    def list_hackers(self):
        cursor = self.conn.cursor()
        hackers = cursor.execute(self.sql_hackers_query).fetchone()[0]
        return hackers
    
    def get_hacker(self, hacker_id):
        cursor = self.conn.cursor()
        hacker = cursor.execute(f'{self.sql_hackers_query} WHERE id=\'{hacker_id}\'').fetchone()[0]
        if len(hacker) < 3:
            return "{\"response\": \"Sorry, but we could not find a hacker with that id.\"}"
        return hacker
    
    def update_hacker(self, hacker_id, data):
        cursor = self.conn.cursor()
        for field in data.keys():
            if field in ['name', 'company', 'email', 'phone']:
                cursor.execute(f'UPDATE hackers SET {field} = \'{data[field]}\' WHERE id = {hacker_id}')
            elif field == 'skills':
                for skill in data['skills']:
                    cursor.execute('INSERT OR IGNORE INTO skills(name) VALUES(?)', [skill['skill']])
                    cursor.execute('INSERT OR REPLACE INTO skill_hacker_join(hacker_id,skill,rating) VALUES(?,?,?)', [hacker_id,skill["skill"],skill["rating"]])

        self.conn.commit()
        return self.get_hacker(hacker_id=hacker_id)
    
    def num_hackers(self):
        cursor = self.conn.cursor()
        return int(cursor.execute("SELECT COUNT(id) FROM hackers").fetchone()[0])

    def list_skill_frequencies(self, min, max):
        cursor = self.conn.cursor()
        sql_frequency = 'SELECT COUNT(hacker_id) FROM skill_hacker_join WHERE skill=name'
        sql_skills = f'''SELECT json_group_array(json_object(
            \'skill\', name,
            \'frequency\', ({sql_frequency})))
            FROM skills WHERE ({sql_frequency}) >= {min} AND ({sql_frequency}) <= {max}'''
        return cursor.execute(sql_skills).fetchone()[0]
    
    def list_events(self):
        cursor = self.conn.cursor()
        events = cursor.execute(self.sql_events_query).fetchone()[0]
        return events

    def get_event(self, event_id):
        cursor = self.conn.cursor()
        event = cursor.execute(f'{self.sql_events_query} WHERE id=\'{event_id}\'').fetchone()[0]
        if len(event) < 3:
            return "{\"response\": \"Sorry, but we could not find an event with that id.\"}"
        return event      
    
    def handle_scan(self, event_id, hacker_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(f'INSERT OR IGNORE INTO event_hacker_join(hacker_id,event_id) VALUES(?,?)', [str(hacker_id),str(event_id)])
            self.conn.commit()
        except:
            return "{\"reponse\": \"invalid id(s) entered\"}"
        return self.list_events()
    
    def handle_registration(self, hacker_id):
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE hackers SET registered=\'true\' WHERE id = \'{hacker_id}\'')
        self.conn.commit()
        return self.get_hacker(hacker_id=hacker_id)
