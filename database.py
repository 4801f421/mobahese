import mysql.connector

class Database:
    def __init__(self, config):
        self.connection = mysql.connector.connect(**config)
        self.cursor = self.connection.cursor(dictionary=True)

    def get_surahs(self):
        query = "SELECT * FROM surahs ORDER BY number"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_ayahs_proc(self, surah_id, start, end):
        query = "SELECT process_text FROM ayahs WHERE surah_id = %s AND number_in_surah BETWEEN %s AND %s"
        self.cursor.execute(query, (surah_id, start, end))
        return [row['process_text'] for row in self.cursor.fetchall()]

    def get_ayahs(self, surah_id, start, end):
        query = "SELECT text FROM ayahs WHERE surah_id = %s AND number_in_surah BETWEEN %s AND %s"
        self.cursor.execute(query, (surah_id, start, end))
        return [row['text'] for row in self.cursor.fetchall()]

    def close(self):
        self.connection.close()
