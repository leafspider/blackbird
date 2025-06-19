from raven.city.page import Page
import requests
from raven.city.database import Database
from os import makedirs
from os.path import exists
import json
import csv

debug = True
# max_pages = 5
max_datasets = 10
max_rows = 10

class Catalogue:
    
    def __init__(s, db: Database=None, debug=False):

        s.debug = debug
        # s.base_url = "https://open.toronto.ca/catalogue/"
        s.base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
        s.db = db
        if s.db is None:
            s.db = Database("city.db")
        s.page_dir = s.db.base_dir + '/page'
        s.dataset_dir = s.db.base_dir + '/dataset'
        if not exists(s.dataset_dir):
            makedirs(s.dataset_dir)

    # def get_pages(s):
        
    #     pages = []
    #     max = max_pages if s.debug else 52
    #     for val in range(0, max):            
    #         page = Page(page_dir=s.page_dir)
    #         soup = page.get_soup(s.base_url + '?n=' + str(val))        
    #         pages.append(soup)   
    #     print("---pages", len(pages))     
    #     return pages

    def get_dataset_ids(s):
                
        # ids = []
        # n = 0
        # pages = s.get_pages()
        # for page in pages:
        #     n += 1
        #     print("page", n)
        #     cards = page.find_all("div", class_="cat-dataset-card")
        #     for card in cards:
        #         id = card.get('id')
        #         ids.append(id)
        #     print("---dataset_ids", len(ids))

        json_path = s.page_dir + "/package_list.json"
        
        if exists(json_path):
            with open(json_path, "r", encoding="utf-8") as json_file:
                package = json.load(json_file)
        else:
            url = s.base_url + "/api/3/action/package_list"
            package = requests.get(url).json()            
            with open(json_path, "w", encoding="utf-8") as json_file:
                json.dump(package, json_file, indent=4)

        ids = []
        for id in package["result"]:    
            ids.append(id)
        return ids

    def get_csv_path(s, id):
        return s.dataset_dir + "/" + str(id) + ".csv"

    def get_dataset(s, id):
        
        url = s.base_url + "/api/3/action/package_show"
        csv_path = s.get_csv_path(id)
        if not exists(csv_path):

            print("get", id)

            # Datasets are called "packages". Each package can contain many "resources"
            # To retrieve metadata for a package and its resources, use the package name in the page's URL:
            params = { "id": id }
            package = requests.get(url, params=params).json()

            # To get resource data:
            for idx, resource in enumerate(package["result"]["resources"]):
        
                # for datastore_active resources:
                if resource["datastore_active"]:
        
                    # To get all records in CSV format:
                    url = s.base_url + "/datastore/dump/" + resource["id"]
                    resource_dump_data = requests.get(url).text
                    with open(csv_path, "w", encoding="utf-8") as csv_file:
                        csv_file.write(resource_dump_data)        
                    # # To selectively pull records and attribute-level metadata:
                    # url = base_url + "/api/3/action/datastore_search"
                    # p = { "id": resource["id"] }
                    # resource_search_data = requests.get(url, params = p).json()["result"]
                    # json_file_path = dataset_path + str(id) + ".json"
                    # with open(json_file_path, "w", encoding="utf-8") as json_file:
                    #     json.dump(resource_search_data, json_file, indent=4)
                    # # API call parameters: https://docs.ckan.org/en/latest/maintaining/datastore.html                
                    return True        
                else:
                    # # To get metadata for non datastore_active resources:
                    # url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
                    # resource_metadata = requests.get(url).json()
                    # with open(json_path, "w", encoding="utf-8") as json_file:
                    #     json.dump(resource_metadata, json_file, indent=4)
                    # # From here, you can use the "url" attribute to download this file
                    print("NOT_ACTIVE id:", id)
                    with open(csv_path, "w", encoding="utf-8") as csv_file:
                        csv_file.write("NOT_ACTIVE")
                return False
            else:
                print("NO_DATA id:", id)
                with open(csv_path, "w", encoding="utf-8") as csv_file:
                    csv_file.write("NO_DATA")
                return False
            
        return True

    def populate(s):    

        ids = s.get_dataset_ids()
        print("---ids", len(ids))
        datasets = []
        max = max_datasets if s.debug else len(ids)
        num = 0
        for id in ids:
            print(str(num+1), id)
            if s.get_dataset(id):
                if s.insert_dataset(id):
                    datasets.append(id)
            num+= 1
            if num >= max:
                break
        return datasets
    
    def insert_dataset(s, id):

        table_name = s.db.clean_table_name(id)

        n, max = 0, max_rows
        csv_file_path = s.get_csv_path(id)

        try:
            with open(csv_file_path, "r", encoding="utf-8", newline='') as file:

                table_exists = False
                cols = []

                reader = csv.reader(file)
                is_first = True
                for row in reader:
                    if row[0] == "NOT_ACTIVE":
                        # print("NOT_ACTIVE id:", id)
                        return False
                    if is_first:
                        cols1 = row
                        for col in cols1:
                            cols.append( s.db.clean_column_name(col) )
                        # print(cols)
                        is_first = False
                    else:
                        vals = row
                        if len(cols) < 1 or len(vals) < len(cols):
                            print("BAD_DATA id:", id, "cols:", len(cols), "vals:", len(vals))
                            return False

                        dict = s.db.to_row(cols, vals)
                        if not table_exists:                        
                            # print("create", table_name)
                            s.db.create_table(table_name, dict)  # create table
                            table_exists = True                    
                        # print("insert", dict)
                        s.db.insert_row(table_name, dict)    # insert dict
                    n += 1
                    if s.debug and (n >= max):
                        break

                # for line in file:
                #     line = line.rstrip()
                #     if line.startswith("_id,"):
                #         cols1 = line.split(",")
                #         cols = []
                #         for col in cols1:
                #             cols.append( s.db.clean_col(col) )
                #     else:
                #         vals = line.split(",")                    
                #         row = s.db.to_row(cols, vals)
                #         if len(cols) < 1 or len(row) < len(cols):
                #             print("BAD_DATA id:", id, "cols:", len(cols), "rows:", len(row))
                #             return False

                #         if not table_exists:                        
                #             # print("create", table_name)
                #             s.db.create_table(table_name, row)  # create table
                #             table_exists = True                    
                #         # print("insert", row)
                #         s.db.insert_row(table_name, row)    # insert row
                #     n += 1
                #     if s.debug and (n >= max):
                #         break
                # print("---rows:", n)
                        
        except Exception as e:            
            print("EXCEPTION id:", id, "e:", e)
            return False
        
        return True


if __name__ == "__main__":

    cat = Catalogue(debug=True)

    # pages = get_pages()
    # print("pages", len(pages) )
    # ids = get_dataset_ids()
    # print("ids", len(ids) )
    # print( db.clean_table( "toronto-island-ferry-ticket-counts" ) )

    datasets = cat.populate()

    # print("datasets", len(datasets) )
    # datasets = cat.insert_dataset("business-improvement-areas")
    
    print("")

    for id in datasets:
        table_name = cat.db.clean_table_name( id )
        # print("dataset:", id)
        # print("table_name", table_name)
        # print(cat.db.tabulate_table(table_name) )
        # print(table_name, cat.db.all_columns(table_name) )
        print(table_name, cat.db.top(table_name) )
        # print(id, cat.db.regressable_columns(table_name) )
    
    # cat = Catalogue(debug=True)
    # print(cat.db.tabulate_table("tl_9425a29e_6b01_40f0_94c2_9a7b9efe8696"))
    