import re
import glob
import os.path
import statistics
from  tkinter import Tk, filedialog
import timeit

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
                    splited = [ data.strip() for data in re.split(split_regex, line.strip())]
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
            filename = re.split(r"[\\ \/]", file_path)[-1]
            result  += [ [filename] + column_data for column_data in Parse.csv(file_path, columns=columns, start_row=start_row, delimiters = delimiters, translate = True)]

        max_row_count = max([ len(column_data) for column_data in result])
        for column_data in result:
            _ = [ column_data.append("") for delta_row in range(max_row_count - len(column_data))]

        return Parse._list_translate(result, column_counts= len(result[0]))


    def list_translate(data_list):
            return Parse._list_translate(data_list)

    def _list_translate(data_list, column_counts = None):
            column_counts = column_counts if column_counts else max([len(row_data) for row_data in data_list])
            return [ [ data_list[row][column] for row in range(len(data_list))] for column in range(column_counts)]

    def file_in_path(folder_path, suffix = "csv"):
        result = []
        if not os.path.isdir(folder_path):
            raise FileExistsError()

        suffix = (suffix if isinstance(suffix, (list, tuple, set)) else [suffix])
        groups = [ glob.glob( "%s/*.%s" % (folder_path, ext)) for ext in suffix]
        for group in groups :
            result += group
        return result
    
    def _format_into_string(data_list, show_index = True, pretty = True, delimiter = ", "):
        result       = []
        column_width = []
        if pretty:
            for row, row_data in enumerate(data_list):
                if not(column_width):
                    column_width = [0 for column in range(len(row_data))]

                for column, column_data in enumerate(row_data):
                    column_width[column] = len(str(column_data)) if (column_width[column] < len(str(column_data))) else column_width[column] 

            index_rjust = len(str(len(data_list)))
            for row, row_data in enumerate(data_list):
                row_string = delimiter.join([str(column_data).rjust(column_width[column]) for column, column_data in enumerate(row_data)])
                if show_index:
                    row_string = delimiter.join([str(row).rjust(index_rjust), row_string])
                result.append(row_string)
        else:
            for row, row_data in enumerate(data_list):
                row_string = delimiter.join([str(column_data) for column, column_data in enumerate(row_data)])
                if show_index:
                    row_string = delimiter.join([str(row), row_string])
                result.append(row_string)

        return ("\n".join(result))

    def out(filename, *args, **kwargs): 
        results = Parse._format_into_string(*args, **kwargs)
        with open(filename, 'w+') as csvfile:
            csvfile.write(results)

    def print(*args, **kwargs):
        print( Parse._format_into_string(*args, **kwargs))


class Statistic(object):
    def __init__(self, data_list, title, parent=None):
        self._data_list          = None
        self._trimmed_data_list  = None
        self._in_spec_data_list  = None
        self._spec_high          = None
        self._spec_low           = None
        self._out_of_spec        = None
        self._uniformaty         = None
        self._avg                = None
        self._std                = None
        self._trimmed_avg        = None
        self._trimmed_std        = None
        self._trimmed_uniformaty = None
        self._outlier            = None
        self._title              = title
        self.data_list           = data_list


    def _isnumeric(data):
        try:
            data = data.strip() if type(data)==str else data
            if len(data) > 0:
                return type(float(data)) == float
            return False
        except: 
            return False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def data_list(self):
        return self._data_list

    @data_list.setter
    def data_list(self, data_list):
        self._data_list         = list(filter(lambda x: (Statistic._isnumeric(x)), data_list))

    def _gen_trim_data_list(self):
        self._trimmed_data_list = list(filter(lambda x: (x >= self.avg - (3 * self.std)) and ( x <= self.avg + (3 * self.std)), self._data_list))
    
    def _gen_in_spec_data_list(self):
        self._in_spec_data_list = list(filter(lambda x: x >= spec_high, self_data_list))        

    @property
    def spec_high(self):
        return self._spec_high

    @spec_high.setter
    def spec_high(self, spec_high):
        self._spec_high = spec_high
        self._gen_in_spec_data_list()

    @property
    def spec_low(self):
        return self._spec_low

    @spec_low.setter
    def spec_low(self, spec_low):
        self._spec_low = spec_low
        self._gen_in_spec_data_list()

    @property
    def in_spec_data_list(self):
        return self._in_spec_data_list

    @property
    def in_spec_avg(self):
        return self.statistics.mean(self.in_spec_data_list)  if len(self.in_spec_data_list) > 0 else None

    @property
    def in_spec_std(self):
        return self.statistics.stdev(self.in_spec_data_list) if len(self.in_spec_data_list) > 0 else None

    @property
    def out_of_spec(self):
        if (self._in_spec_data_list==None):
            self._gen_in_spec_data_list()
        self._out_of_spec = (len(self._data_list) - len(self._in_spec_data_list))
        return self._out_of_spec


    @property
    def avg(self):
        self._avg = statistics.mean(self._data_list)  if len(self) > 0 else None
        return self._avg

    @property
    def std(self):
        self._std = statistics.stdev(self._data_list) if len(self) > 0 else None
        return self._std

    @property
    def trimmed_avg(self):
        if (self._trimmed_data_list==None):
            self._gen_trim_data_list()
        self._trimmed_avg = statistics.mean(self._trimmed_data_list) if len(this._trimmed_data_list) > 0 else None
        return self._trimmed_avg

    @property
    def trimmed_std(self):
        if (self._trimmed_data_list==None):
             self._gen_trim_data_list()
        self._trimmed_std = statistics.stdev(self._trimmed_data_list) if len(this._trimmed_data_list) > 0 else None
        return self._trimmed_std

    @property
    def outlier(self):
        if (self._trimmed_data_list==None):
             self._gen_trim_data_list()
        self._outlier = (len(self._data_list) - len(self._trimmed_data_list))
        return self._outlier
        
    @property
    def frequency_chart(scale = []):
        result    = {}
        data_list = self._data_list
        
        if not scale:
            scale = (min(data_list), max(data_list), (max(data_list)-min(data_list)/10))

        start, stop, step = scale
        sections          = int(( stop - start ) / step)

        _ = [ result.update( { (start + (step * segment)) : 0 } )  for segment in range(sections)]

        for data in data_list:
            index = start + (step * int((data-start)/step))
            key   = list(result.keys())
            index = key[0]  if index < key[0] else ( key[-1] if index > key[-1] else index)
            result[index] += 1

        return [[key, value] for key, value in result.items()]
        
    def __len__(self):
        return len(self._data_list)

    def __str__(self):
        return """
      title: %s
         +3: %f
        avg: %f
         -3: %f
        std: %f
    outlier: %d pts
trimmed_avg: %f
trimmed_std: %f
  spec_high: %f
   spec_low: %f
in_spec_avg: %f
in_spec_std: %f
""" % (self.title, (self.avg + (3*self.std)), self.avg, (self.avg - (3*self.std)), self.std, self.outlier, self.trimmed_avg, self.trimmed_std, self.spec_high, self.spec_low, self.in_spec_avg, self.in_spec_std)


        






class File(object):
    file_types = (("csv files","*.csv"),("txt files","*.txt"),("all files","*.*"))

    def open_file_dialog():
        root = Tk()
        root.withdraw()
        return filedialog.askopenfilename(initialdir = "/",title = "Select file", filetypes = File.file_types)

    def open_path_dialog():
        root = Tk()
        root.withdraw()
        return filedialog.askopenfilename(initialdir = "/",title = "Select folder", filetypes = File.file_types)

    def save_file_dialog():
        root = Tk()
        root.withdraw()        
        return tkFileDialog.asksaveasfilename(initialdir = "/",title = "Select file", filetypes = File.file_types)





file_name = "C:/Users/rawr/Downloads/MOCK_DATA.csv"
# file_list = Parse.file_in_path("C:/Users/rawr/Downloads/")
# result_a  = Parse.multiple_csv(file_list, 0, [3])
reslut_b  = [data[0] for data in Parse.csv(file_name, 0, [6])]
# Parse.print(Parse.list_translate(reslut_b))
# Parse.print(result_a, False, False)
# # print(Parse.unit("a"))

# (?# file_name = r"C:\Users\rawr\Desktop\rk\1NJF299.1_01_CP1.csv")
# file_list = Parse.file_in_path(r"C:\Users\rawr\Desktop\rk")
# result_a  = Parse.multiple_csv(file_list, 10, [2, 3, 4])
# Parse.print(result_a)
# reslut_b  = Parse.csv(file_name, 10, [2, 3, 4])
# Parse.print(reslut_b)
# file_name ='C:/Users/rawr/Desktop/a.csv'# File.open_file_dialog()
# print (file_name)
# d_data = [float(*row_data) for row_data in Parse.csv(file_name)]
# s = Statistic(d_data)

# print (s)
# print(reslut_b)

if __name__ == '__main__':
    import timeit
    def k():
        m=[ float(data) for data in reslut_b if Statistic._isnumeric(data) ]

    def q():
        m=list(filter(lambda x: (Statistic._isnumeric(x)), reslut_b))


    print(timeit.timeit(stmt='k()', number=5000, setup="from __main__ import k"))
    print(timeit.timeit(stmt='q()', number=5000, setup="from __main__ import q"))
# print(m)