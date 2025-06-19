import sqlite3
import re
from tabulate import tabulate
from os import getcwd, makedirs
from os.path import exists


class Database:

    def __init__(s, file_name, base_dir=getcwd() + '/data'):
    
        s.base_dir = base_dir
        s.db_dir = s.base_dir + '/db'
        if not exists(s.db_dir):
            makedirs(s.db_dir)

        s.db_path = s.db_dir + '/' + file_name
        print(s.db_path)

        s.conn = sqlite3.connect(s.db_path)

    def __del__(s):
        s.conn.close()

    def query(s, query):

        #s.conn.row_factory = sqlite3.Row
        res = s.conn.cursor().execute( query )
        #for item in res:
        #    print( item )
        return res

    def to_row(s, cols, vals):
        
        return dict(zip(cols, vals))

    def insert_row(s, table, row):

        keys = ','.join(row.keys())
        question_marks = ','.join(list('?' * len(row)))
        values = tuple(row.values())
        # print(values)
        return s.conn.cursor().execute('INSERT INTO ' + table + ' (' + keys + ') VALUES (' + question_marks + ')', values)
    
    def commit(s): 
        s.conn.commit()

    def create_table(s, table_name, row):

        sql = s.get_create_sql( table_name, row)
        print(sql)
        try:
            c = s.conn.cursor()
            c.execute( sql )
            s.conn.commit()
        except:
            print("Error sql", sql)
        return sql

    def get_create_sql(s, table, row):

        cols_to_create = {}
        for key in row.keys():
            val = str(row[key])
            col_type = 'text'
            if val.isnumeric():
                col_type = 'integer'
            elif s.isfloat(val):
                col_type = 'real'
            cols_to_create[key] = col_type

        col_text = ''
        for key in cols_to_create.keys():
            if col_text == '':
                # Assume first column is id
                col_text += key + " " + cols_to_create[key] + " PRIMARY KEY"
            else:
                col_text += ", " + key + " " + cols_to_create[key]

        return "CREATE TABLE IF NOT EXISTS " + table + "(" + col_text + ")"

    def isfloat(s, str):
        try:
            float(str)
        except ValueError:
            return False
        return True

    def clean_table_name(s,x):
        # return "tl_" + re.sub(r"[() \-%/*.<>+]","_", x).lower()
        return "_" + s.sanitize(x)

    def clean_column_name(s,x):
        # return "cl_" + re.sub(r"[() \-%/*.<>+]","_", x).lower()
        return "_" + s.sanitize(x)
    
    def sanitize(s,x):
        return re.sub(r'[^A-Za-z0-9_]', '_', x).lower()

    def clean_value(s,x):
        if type(x) == str:
            return re.sub(r'[*+%]', '', x)
        else:
            return x

    def tabulate_columns(s, table):
        res = [s.all_columns(table)]
        return tabulate(res, tablefmt='outline')

    def tabulate_table(s, table):
        res = [s.all_columns(table)]
        res.extend( s.select_all(table) )
        print(res)
        return tabulate(res, tablefmt='outline')
    
    def select_all(s, table):
        return list( s.query("SELECT * FROM " + table) )

    def top(s, table_name, n=1, cols=None):
        if cols is None:
            res = s.query("SELECT * FROM %s limit %d" % (table_name, n))
        else:
            res = s.query("SELECT %s FROM %s limit %d" % (','.join(cols), table_name, n))
        return list(res.fetchall())

    def all_columns(s, table_name):
        res = s.query("SELECT * FROM %s limit 1" % table_name)
        return [d[0] for d in res.description]

    def all_tables(s):
        res = s.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [d[0] for d in res]
    
    def table_exists(s, table_name):
        res = s.query("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % table_name)
        return len(res.fetchall()) > 0
    
    def drop_table(s, table_name):
        res = s.query("DROP TABLE IF EXISTS %s" % table_name )
        s.conn.commit()

    # @staticmethod
    # def test():
    #     data = DataStore()
    #     # data.query("DELETE FROM rosters")
    #     data.build()
    #     # nfl.db.game_scores.GameScores.test()

if __name__ == '__main__':

    # db = DataBase("city.db")

    # tables = db.all_tables()
    # print("tables", tables)
    # for table in tables:
    #     # print(table)
    #     print(table, len(db.top_row(table)), db.all_columns(table)[0:2])
    #     # print("")
    # print("tables", len(tables))

    # table_name = "t_bicycle_thefts"
    # table_name = db.clean_table("active-affordable-and-social-housing-units")
    # print(db.all_columns(table_name))    
    # print(db.top(table_name))
    # print(db.top(table_name, 3))
    # # print(db.select_all(table_name))
    # res = db.query("SELECT * FROM %s limit 1" % table_name)
    # res = [d[0] for d in res]
    # print( type(res) )
    # print(db.tabulate_table(table_name))
    # print(len(db.select_all(table_name)))
    # print(db.top(table_name))

    base_dir = getcwd() + '/data_test'

    db_name = "test5.db"
    db = Database(db_name, base_dir)

    table_name = "my_table"
    row = {"c__id": 2353454, "col1": 2, "col2": "trout", "col3": 2.5, "year": 2025}
    db.create_table(table_name, row)
    db.insert_row(table_name, row)

    # print(db.all_tables())
    # print(db.top(table_name))
    # print(db.all_columns(table_name))
    # print( db.select_all(table_name))