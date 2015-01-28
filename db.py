import pg8000

class Db:
    def __init__(self):
        self.conn = pg8000.connect(user="postgres", password="postgres", database="700level")
        self.cursor = self.conn.cursor()

    def _get_markov_columns(self, depth):
        columns = []
        columns.append("author")
        for x in range(1,depth+1):
            columns.append("word_" + str(x))
        columns.append("frequency")
        columns.append("project_name")
        return ','.join(i for i in columns)

    def add_markov_chain(self, author, project, depth, word_list):
        #set up column sql
        columns = self._get_markov_columns(depth)

        #set up values sql
        values = []
        values.append(author)
        values.append(word_list[0])
        values.append(word_list[1])
        values.append(1)
        values.append(project)
        value_string = ','.join('%s' for i in values)

        #assemble and execute
        sql = "INSERT INTO word_2_tuples (%s) VALUES (%s)" % (columns, value_string)
        self.cursor.execute(sql, values)
        self.conn.commit()
