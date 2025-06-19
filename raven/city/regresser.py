
import numpy as np
from sklearn.linear_model import LinearRegression
from regression_db import *
from tabulate import tabulate
from regression_db import *


class Regresser:

    def __init__(s, data):

        s.data: RegressionDatabase = data

    def score(self, x, y):

        x = np.array(x).reshape((-1, 1))
        # y = [[int(z.strip() or '0') if type(z) == str else z for z in sl] for sl in y]  # handle empty strings
        y = [[z for z in sl] for sl in y]  # handle empty strings
        y = np.array(y)
        # print("score:", x, y)
        model = LinearRegression().fit(x, y)
        return model.score(x, y)       # Coefficient of determination R^2

    def compare_all_columns(s, table_x, table_y, r2_threshold):

        cols_y = s.data.analyzable_columns(table_y)
        if len(cols_y) == 0:
            # print("No analyzable columns in", table_y)
            return []

        matrix = [[]]
        matrix[0] = [table_y + '.' + f'{i}' for i in cols_y]
        matrix[0].insert(0, '-')

        cols_x = s.data.analyzable_columns(table_x)
        
        # print("tables:", table_x, table_y)
        for col_x in cols_x:

            x_vals = list(s.data.query("SELECT " + col_x + " FROM " + table_x ))

            all_are_nums = all( [isinstance(x[0], (int, float)) for x in x_vals] )
            if not all_are_nums:
                # print("Not all numbers:", col_x, x_vals)
                continue
            
            row = [table_x + '.' + col_x]

            for col_y in cols_y:
                y_query = "SELECT " + col_y + " FROM " + table_y
                y_vals = list(s.data.query(y_query))
                
                if len(x_vals) != len(y_vals):
                    # print("Not same length:", len(x_vals), len(y_vals))
                    row.append(None)
                    continue

                all_are_nums = all( [isinstance(y[0], (int, float)) for y in y_vals] )
                if not all_are_nums:
                    # print("Not all numbers:", col_y, y_vals)
                    row.append(None)
                    continue

                score = s.score(x_vals, y_vals)
                if score > r2_threshold:
                    row.append( '{0:.4f}'.format(score) )
                else:
                    row.append(None)       
     
            matrix.append(row)

        return matrix

    def compare_tables(s, table_x, tables_y, r2_threshold=0.25):

        cols_x = s.data.analyzable_columns(table_x)
        if len(cols_x) == 0:
            # print("No analyzable columns in", table_x)
            return []

        matrix = []
        for table_y in tables_y:
            m = s.compare_all_columns(table_x, table_y, r2_threshold)
            # print(len(m[7]), m[7])
            if len(m) == 0:
                continue
            try:
                m = np.transpose(m)
            except ValueError as ve:
                print("ValueError:", m)
                raise ve                   
                # continue
            m = np.ndarray.tolist(m)
            if len(matrix) == 0:
                matrix.extend([m[0]])  # column names
            matrix.extend(m[1:])

        # remove empty rows
        matrix_2 = []
        for row in matrix:
            vals = row[1:]
            if next((item for item in vals if item is not None), 'AllNone') == 'AllNone':
                continue
            else:
                matrix_2.extend([row])

        # remove empty columns
        matrix_2 = np.transpose(matrix_2)
        matrix = []
        for row in matrix_2:
            vals = row[1:]
            if next((item for item in vals if item is not None), 'AllNone') == 'AllNone':
                continue
            else:
                matrix.extend([row])

        # print(tabulate(matrix,tablefmt='outline'))

        tables_x = matrix[0][1:]
        tables_y = np.transpose(matrix)[0][1:]

        weights = []

        for col in range(len(tables_x)):
            for row in range(len(tables_y)):
                val = matrix[row + 1][col + 1]
                if not val is None:
                    table_x = tables_x[col]
                    table_y = tables_y[row]
                    weight = {'table_x': table_x, 'table_y': table_y, 'r2': val}
                    weights.append( weight )
                    #print( weight )

        return weights

    # @staticmethod
    # def test():
    #     print("Testing Regresser")

    #     data = nfl.db.data_store.DataStore()

    #     regresser = nfl.regresser.Regresser(data)
    #     stats_tables = nfl.db.team_stats.TeamStats.stat_table
    #     weights = regresser.calculate_weights('team_standings', stats_tables, 0.09)


if __name__ == '__main__':
    
    db = RegressionDatabase("city.db")

    # print(db.analyzable_columns("_address_points_municipal_toronto_one_address_repository"))

    # table_name = "_address_points_municipal_toronto_one_address_repository"
    # cols = db.analyzable_columns(table_name)
    # print(cols)
    # print( db.top(table_name, cols=cols) )
    # col_name = "_address_number"
    # print( list(db.query("SELECT " + col_name + " FROM " + table_name )))

    regresser = Regresser(db)

    # all_tables = db.all_tables()
    # iter = iter(all_tables)
    # n = 0
    # for table in iter:
    #     this_table = next(iter)
    #     print("table:", this_table)
    #     other_tables = [x for x in all_tables if x != this_table]
    #     weights = regresser.compare_tables(this_table, other_tables, 0.09)
    #     # print(weights)
    #     if len(weights) > 2:
    #         n += 1
    #         if n > 5:
    #             print(tabulate(weights,tablefmt='outline'))
    #             break
    
    # y_vals = [(15,), (7,), ('61A',), (1,), (42,), (5,), (34,), (49,), (7,)]
    # # y_vals = [15, 7, '61A', 1, 42, 5, 34, 49, 7]
    # # are_nums = [lambda y: isinstance(y, (int, float)), y_vals]
    # are_nums = [isinstance(y[0], (int, float)) for y in y_vals]
    # print("are_nums:", are_nums)
    # print("all are_nums:", all(are_nums))

    this_table = "_bicycle_thefts"
    other_tables = ["_address_points_municipal_toronto_one_address_repository"]
    weights = regresser.compare_tables(this_table, other_tables, 0.09)
    for weight in weights:
        print(weight['r2'], weight['table_x'], weight['table_y'])

    # m = [['-', '_address_points_municipal_toronto_one_address_repository._address_point_id', '_address_points_municipal_toronto_one_address_repository._address_id', '_address_points_municipal_toronto_one_address_repository._address_string_id', '_address_points_municipal_toronto_one_address_repository._linear_name_id', '_address_points_municipal_toronto_one_address_repository._centreline_id', '_address_points_municipal_toronto_one_address_repository._address_number', '_address_points_municipal_toronto_one_address_repository._lo_num', '_address_points_municipal_toronto_one_address_repository._centreline_measure', '_address_points_municipal_toronto_one_address_repository._centreline_offset', '_address_points_municipal_toronto_one_address_repository._general_use_code', '_address_points_municipal_toronto_one_address_repository._class_family', '_address_points_municipal_toronto_one_address_repository._objectid', '_address_points_municipal_toronto_one_address_repository._ward'], ['_bicycle_thefts._occ_day', None, None, '0.3340', '0.1657', '0.4504', None, '0.1836', None, None, '1.0000', '1.0000', '0.2865', '1.0000'], ['_bicycle_thefts._occ_doy', None, None, '0.4085', '0.1608', '0.3586', None, '0.1334', None, None, '1.0000', '1.0000', '0.2185', '1.0000'], ['_bicycle_thefts._occ_hour', None, None, None, '0.2148', None, None, None, None, '0.1762', '1.0000', '1.0000', '0.3336', '1.0000'], ['_bicycle_thefts._report_day', '0.1068', '0.2368', '0.1351', '0.3847', None, None, None, None, '0.1641', '1.0000', '1.0000', '0.7404', '1.0000'], ['_bicycle_thefts._report_doy', '0.1068', '0.2368', '0.1351', '0.3847', None, None, None, None, '0.1641', '1.0000', '1.0000', '0.7404', '1.0000'], ['_bicycle_thefts._report_hour', None, '0.2799', '0.1762', '0.2496', '0.3190', None, '0.1951', None, '0.3111', '1.0000', '1.0000', None, '1.0000'], ['_bicycle_thefts._bike_speed', None, None, '0.2771', '0.1323', '0.3304', None, None, None, None, '1.0000', '1.0000', '0.3055', '1.0000', None], ['_bicycle_thefts._long_wgs84', None, '0.3791', None, '0.7980', None, None, '0.1762', '0.2202', None, '1.0000', '1.0000', None, '1.0000'], ['_bicycle_thefts._lat_wgs84', '0.1291', None, '0.2863', '0.1615', '0.1221', None, None, '0.3059', None, '1.0000', '1.0000', '0.2109', '1.0000']]
    # print(m[6])
    # print(m[7])
    # m = np.transpose(m)

    # x = [[657],[667],[678],[681],[694],[700],[711],[713],[723]] 
    # y = [[16.32],[16.66],[16.71],[18.61],[20.82],[21.09],[23.96],[24.88],[28.7]]
    # x = [657,667,678,681,694,700,711,713,723] 
    # y = [16.32,16.66,16.71,18.61,20.82,21.09,23.96,24.88,25.7]
    
    # print("score:", regresser.score(x, y))