import re
import glob
import os.path


class Parse(object):
    derived_unit_dict = {
        ""  : 1, 
        "T" : 1E12, "G" :  1E9, "M" :  1E6, "K" :  1E3,
        "m" : 1E-3, "u" : 1E-6, "n" : 1E-9, "p" : 1E-12}

    derived_unit_regex = r"^([-0-9 .]+)([%s]|)" % "".join([ u for u in derived_unit_dict.keys()])


    def unit(data_str, out_fmt = "%.3e", if_error = None):
        matched = re.match(Parse.derived_unit_regex, data_str.strip())
        if matched:
            value, derived_unit = matched.groups(0)
            try:
                return out_fmt % (float(value) * Parse.derived_unit_dict[derived_unit])
            except:
                pass
        print("* parse error with data: %s     regex: %s" % (data_str, Parse.derived_unit_regex) )
        return data_str if (if_error==None) else if_error

    def csv(file_path, start_row = 0, columns = [], delimiters = "[,]+", translate = False):
        result         = []
        tresult        = []
        column_counter = []

        if not os.path.isfile(file_path):
            raise FileExistsError()

        split_regex = ("[%s]+" % "".join(set(delimiters))) if isinstance(delimiters, (list, tuple, set)) else delimiters

        with open(file_path) as file:
            for row, line in enumerate(file):
                if row >= start_row:
                    splited = re.split(split_regex, line.strip())
                    if columns:
                        result.append([ data for column, data in enumerate(splited) if column in columns])
                    else:
                        result.append(splited)
                    column_counter.append(len(result[-1]))

        max_column     = max(column_counter)
        column_delta   = [ (max_column-column_count) for column_count in column_counter ]
        if (any(column_delta)):
            for row_index, delta in enumerate(column_delta):
                if delta:
                    _ = [result[row_index].append("") for add_column in range(delta)]

        if translate:
            return Parse._list_translate(result, column_counts = len(columns))

        return result

    def multiple_csv(file_list, start_row = 0, columns = [], delimiters = "[,]+"):
        result = []
        for file_path in file_list:
            filename = re.split(r"[\\\/.]", file_path)[-2]
            result += [ [filename] + column_data for column_data in Parse.csv(file_path, columns=columns, start_row=start_row, delimiters = delimiters, translate = True)]
        return Parse._list_translate(result, column_counts= len(result[0]))


    def list_translate(data_list):
            return Parse._list_translate(data_list)

    def _list_translate(data_list, column_counts = None):
            column_counts = column_counts if column_counts else max([len(row_data) for row_data in data_list])
            return [ [ data_list[row][column] for row in range(len(data_list))] for column in range(column_counts)]

    def file_in_path(folder_path, post_fix = "csv"):
        result = []
        if not os.path.isdir(folder_path):
            raise FileExistsError()

        post_fix = (post_fix if isinstance(post_fix, (list, tuple, set)) else [post_fix])
        groups = [ glob.glob( "%s/*.%s" % (folder_path, ext)) for ext in post_fix]
        for group in groups :
            result += group
        return result
    
    def print(data_list, show_index = True, pretty = True):
        result       = []
        column_width = []

            for row, row_data in enumerate(data_list):
                if not(column_width):
                    column_width = [0 for column in range(len(row_data))]

                for column, column_data in enumerate(row_data):
                    column_width[column] = len(column_data) if (column_width[column] < len(column_data)) else column_width[column] 


        
        index_rjust = len(str(len(data_list)))
        for row, row_data in enumerate(data_list):
            row_string = ", ".join([column_data.rjust(column_width[column])for column, column_data in enumerate(row_data)])
            if show_index:
                row_string = str(row).rjust(index_rjust) + ", " + row_string
            result.append(row_string)

        print ("\n".join(result))


# file_name = "C:/Users/rawr/Downloads/MOCK_DATA.csv"
file_list = Parse.file_in_path("C:/Users/rawr/Downloads/")
result_a  = Parse.multiple_csv(file_list, 0, [3])
# reslut_b  = Parse.csv(file_name, 0, [1,4])
# Parse.print(Parse.list_translate(reslut_b))
Parse.print(result_a, False)
# print(Parse.unit("a"))