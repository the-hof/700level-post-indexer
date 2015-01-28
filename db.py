import pg8000

class Db:
    def __init__(self, project, depth):
        self.project = project
        self.depth = depth
        self.conn = pg8000.connect(user="postgres", password="postgres", database="700level")
        self.cursor = self.conn.cursor()
        self._setup(project, depth)

    def _setup(self, project, depth):
        tuples_table_name = self._get_tuples_table_name(depth)
        stats_table_name = self._get_stats_table_name()
        tuples_sql = "DELETE FROM %s WHERE project_name = '%s'" % (tuples_table_name, project)
        self.cursor.execute(tuples_sql)
        stats_sql = "DELETE FROM %s WHERE project_name = '%s'" % (stats_table_name, project)
        self.cursor.execute(stats_sql)
        self.conn.commit()

    #######################################
    ## MARKOV TUPLES
    #######################################

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
        for x in range(1,len(word_list)+1):
            filter.append(" AND word_" + str(x) + " = %s")
        filter.append(" AND project_name = %s")
        sql = "".join(i for i in filter)
        return sql

    def _get_markov_filter_values(self, author, project, word_list):
        filter_values = []
        filter_values.append(author)
        for x in range(0,len(word_list)):
            filter_values.append(word_list[x])
        filter_values.append(project)
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

    def add_markov_chain(self, author, word_list):
        is_valid = True

        #check lengths of each word and skip any pairs that have unusually long words
        for word in word_list:
            if (len(word) > 100):
                is_valid = False

        if is_valid:
            table_name = self._get_tuples_table_name(len(word_list))
            frequency = self._get_frequency(author, self.project, word_list) + 1

            if frequency == 1:
                #set up column sql
                columns = self._get_markov_columns(len(word_list))
                column_string = ','.join(i for i in columns)

                #set up values sql
                values = self._get_markov_values(author, self.project, frequency, word_list)
                value_string = ','.join('%s' for i in values)

                #assemble and execute

                sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, column_string, value_string)
            else:
                filter_string = self._get_markov_filter_string(word_list)
                values = self._get_markov_filter_values(author, self.project, word_list)

                sql = "UPDATE %s SET frequency = %s WHERE %s" % (table_name, str(frequency), filter_string)

            self.cursor.execute(sql, values)
            self.conn.commit()

    #######################################
    ## RUNNING STATS
    #######################################

    def _get_stats_table_name(self):
        return "stats"

    def _get_stats_columns(self):
        columns = []
        columns.append("author")
        columns.append("project_name")
        return columns

    def _get_stats_values(self, author, project):
        values = []
        values.append(author)
        values.append(project)
        return values

    def _get_stats_filter_string(self):
        filter = []
        filter.append("author = %s")
        filter.append(" AND project_name = %s")
        sql = "".join(i for i in filter)
        return sql

    def _get_stats_filter_values(self, author, project):
        filter_values = []
        filter_values.append(author)
        filter_values.append(project)
        return filter_values

    def _get_stats(self, author, project):
        table_name = self._get_stats_table_name()
        filter_string = self._get_stats_filter_string()
        filter_values = self._get_stats_filter_values(author, project)

        sql = "SELECT word_count, post_count FROM %s WHERE %s" % (table_name, filter_string)

        self.cursor.execute(sql, filter_values)
        r = self.cursor.fetchone()

        if r:
            return r
        else:
            return None

    def update_stats(self, author, post_length):
        table = self._get_stats_table_name()
        words = post_length
        posts = 1

        stats = self._get_stats(author, self.project)

        if stats:
            words = words + stats[0]
            posts = posts + stats[1]
        else:
            #set up column sql
            insert_columns = self._get_stats_columns()
            insert_column_string = ','.join(i for i in insert_columns)

            #set up values sql
            insert_values = self._get_stats_values(author, self.project)
            insert_value_string = ','.join('%s' for i in insert_values)

            insert_sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, insert_column_string, insert_value_string)
            self.cursor.execute(insert_sql, insert_values)
            self.conn.commit()

        filter = self._get_stats_filter_string()
        values = self._get_stats_filter_values(author, self.project)
        sql = "UPDATE %s SET word_count = %s, post_count = %s WHERE %s" % (table, str(words), str(posts), filter)
        self.cursor.execute(sql, values)
        self.conn.commit()
