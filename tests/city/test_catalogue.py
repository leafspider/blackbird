from raven.city.catalogue import *
from os import getcwd

debug=True
base_dir = getcwd() + '/data_test'
file_name = "test_city.db"

    
def test_get_dataset_ids():
    db = Database(file_name, base_dir)
    cat = Catalogue(db, debug)
    ids = cat.get_dataset_ids()
    assert len(ids) > 0

def test_get_create_sql():
    db = Database(file_name, base_dir)
    cat = Catalogue(db, debug)
    ids = cat.get_dataset_ids()
    table_name = cat.db.clean_table_name(ids[0])
    sql = db.get_create_sql(table_name, {"col1": 1, "col2": "bobbins"})
    print(sql)
    assert len(sql) > 0

def test_insert_datasets():
    db = Database(file_name, base_dir)
    cat = Catalogue(db, debug)
    for id in cat.populate():
        table_name = cat.db.clean_table_name(id)
        assert len(cat.db.select_all(table_name)) > 0

def test_tabulate():    
    db = Database(file_name, base_dir)
    cat = Catalogue(db, debug)
    ids = cat.get_dataset_ids()
    max = 2 if debug else len(ids)
    n = 0
    for id in ids:
        table_name = cat.db.clean_table_name(id)
        if db.table_exists(table_name):
            assert len( db.tabulate_columns(table_name) ) > 0
            assert len( db.tabulate_table(table_name) ) > 0
            n += 1
            if n >= max:
                break
