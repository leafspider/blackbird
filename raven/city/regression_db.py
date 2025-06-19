from raven.city.database import Database 
from os import getcwd
from datetime import datetime


class RegressionDatabase(Database):

    def __init__(s, file_name, base_dir=getcwd() + '/data'):
        super().__init__(file_name, base_dir)

    def is_year(s, value):
        # Simple check for between 1900 and current year
        current_year = datetime.now().year
        return isinstance(value, int) and 1900 <= value <= current_year

    def analyzable_columns(s, table_name):
        res = s.query("SELECT * FROM %s limit 1" % table_name)
        cols = [d[0] for d in res.description]
        try:
            vals = list(res)[0]
        except IndexError:
            print("No rows in table:", table_name)
            return []
        new_cols = []
        # Assume first column is id
        for col, val in zip(cols[1:], vals[1:]):
            if isinstance(val, str):
                continue
            elif s.is_year(val):
                # print("is_year:", table_name, col, val)
                continue
            else:
                new_cols.append(col)
        return new_cols

    # def regression(s, threshold):
    #     reg = nfl.regress.regresser.Regresser(s)
    #     reg.populate(threshold)

    # def build(s):
    #     s.populate(2021)
    #     s.regression(0.09)


if __name__ == '__main__':

    base_dir = getcwd() + '/data_test'

    db_name = "test5.db"
    db = RegressionDatabase(db_name, base_dir)

    table_name = "table1"
    row = {"id": 2353454, "col1": 2, "col2": "trout", "col3": 2.5, "year": 2025, "text": "description"}
    
    db.create_table(table_name, row)
    db.insert_row(table_name, row)
    db.commit()

    print(db.all_tables())
    print(db.select_all(table_name))
    # print(db.top(table_name))
    # print(db.all_columns(table_name))
    # print(db.analyzable_columns(table_name))
    # print( db.select_all(table_name))