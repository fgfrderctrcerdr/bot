import sqlite3
connection = sqlite3.connect('datebase.db')
cursor = connection.cursor()
query = '''
        DELETE FROM user_booking_data
        WHERE username = ?
        '''
cursor.execute(query, ('@helloshdev', ))
connection.commit()
connection.close()