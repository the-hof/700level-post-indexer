import pg8000

class Db:
    def __init__(self):
        self.conn = pg8000.connect(user="postgres", password="postgres", database="700level")
        self.cursor = self.conn.cursor()

    def __clean_values__(self, value):
        return value.replace("'","''")

    def add_words(self, author, project, word_list):
        columns = "author, word_1, word_2, frequency, project_name"
        word1 = self.__clean_values__(word_list[0])
        word2 = self.__clean_values__(word_list[1])
        values = "'" + author + "','" + word1 + "','" + word2 + "',1,'" + project + "'"
        values = []
        values.append(author)
        values.append(word_list[0])
        values.append(word_list[1])
        values.append(1)
        values.append(project)
        sql = "INSERT INTO word_2_tuples (author, word_1, word_2, frequency, project_name) VALUES(%s)" % ','.join('%s' for i in values)
        self.cursor.execute(sql, values)
        self.conn.commit()
