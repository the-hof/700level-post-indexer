import pg8000

class Db:
    def __init__(self):
        self.conn = pg8000.connect(user="postgres", password="postgres", database="700level")
        self.cursor = self.conn.cursor()

    def _get_tuples_table_name(self, depth):
        return "word_" + str(depth) + "_tuples"

    def _get_markov_columns(self, depth):
        columns = []
        columns.append("author")
        for x in range(1,depth+1):
            columns.append("word_" + str(x))
        columns.append("frequency")
        columns.append("project_name")
        return columns

    def _get_markov_values(self, author, project, frequency, word_list):
        values = []
        values.append(author)
        for x in range(0, len(word_list)):
            values.append(word_list[x])
        values.append(frequency)
        values.append(project)
        return values

    def _get_markov_filter_string(self, word_list):
        filter = []
        filter.append("author = %s")
        filter.append(" AND project_name = %s")
        for x in range(1,len(word_list)+1):
            filter.append(" AND word_" + str(x) + " = %s")
        sql = "".join(i for i in filter)
        return sql

    def _get_markov_filter_values(self, author, project, word_list):
        filter_values = []
        filter_values.append(author)
        filter_values.append(project)
        for x in range(0,len(word_list)):
            filter_values.append(word_list[x])
        return filter_values

    def _get_frequency(self, author, project, word_list):
        table_name = self._get_tuples_table_name(len(word_list))
        filter_string = self._get_markov_filter_string(word_list)
        filter_values = self._get_markov_filter_values(author, project, word_list)

        sql = "SELECT frequency FROM %s WHERE %s" % (table_name, filter_string)

        self.cursor.execute(sql, filter_values)
        r = self.cursor.fetchone()

        if r:
            return r[0]
        else:
            return 0

    def add_markov_chain(self, author, project, word_list):
        is_valid = True

        #check lengths of each word and skip any pairs that have unusually long words
        for word in word_list:
            if (len(word) > 100):
                is_valid = False

        if is_valid:
            frequency = self._get_frequency(author, project, word_list) + 1

            #set up column sql
            columns = self._get_markov_columns(len(word_list))
            column_string = ','.join(i for i in columns)

            #set up values sql
            values = self._get_markov_values(author, project, frequency, word_list)
            value_string = ','.join('%s' for i in values)

            #assemble and execute
            table_name = self._get_tuples_table_name(len(word_list))
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, column_string, value_string)
            self.cursor.execute(sql, values)
            self.conn.commit()
