from raven.city.catalogue import *
from os import getcwd

base_dir = getcwd() + '/data_test'

def test_get_create_sql():

    db_name = "test1.db"
    db = Database(db_name, base_dir)
    sql = db.get_create_sql("my_table", {"col1": 1, "col2": "bobbins"})
    assert len(sql) > 0

def test_create_table():

    db_name = "test2.db"
    db = Database(db_name, base_dir)
    sql = db.create_table("my_table", {"col1": 1, "col2": "bobbins"})
    assert db.table_exists("my_table")
    assert len(sql) > 0
    db.drop_table("my_table")
    assert not db.table_exists("my_table")
    assert len(db.all_tables()) == 0

def test_insert_row():

    db_name = "test3.db"
    db = Database(db_name, base_dir)
    row = db.to_row(["id", "col1"], [2,"bobbins"])
    db.create_table("my_table", row)
    db.insert_row("my_table", row)
    db.insert_row("my_table", {"id": 3, "col1": "trout"})
    assert len(db.all_columns("my_table")) == 2
    assert len(db.select_all("my_table")) == 2

def test_all():  

    db_name = "test4.db"
    db = Database(db_name, base_dir)
    row = {"col1": 2, "col2": "trout"}

    table_name = "my_table"
    db.create_table(table_name, row)
    assert len(db.all_tables()) > 0
    assert db.all_columns(table_name)[0] == "col1" 

    db.insert_row("my_table", row)
    db.insert_row("my_table", {"col1": 5, "col2": "salmon"})
    assert len(db.top(table_name)) == 1
    assert len(db.top(table_name, 3)) == 2
    assert len( db.select_all(table_name)) == 2

def test_unique():

    db_name = "test5.db"
    db = Database(db_name, base_dir)
    row = db.to_row(["id", "col1", "col2"], [12345, 2,"bobbins"])
    db.create_table("my_table", row)
    db.insert_row("my_table", row)
    assert len(db.select_all("my_table")) == 1
    try:
        db.insert_row("my_table", {"id": 12345, "col1": 2, "col2": "trout"})
    except Exception as e:
        print("EXCEPTION:", e)
        assert str(e) == "UNIQUE constraint failed: my_table.id"
