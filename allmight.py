import re
import glob
import os.path
from pathlib import Path
import statistics
try:
    import cPickle as pickle
except:
    import pickle

from  tkinter import Tk, filedialog


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
    def __init__(self, data, spec_high=None, spec_low=None, title=None, parent=None):

        self._data       = None
        self._uniformaty = None
        self._avg        = None
        self._std        = None
        self._uniformaty = None
        self._outlier    = None
        self._parent     = parent
        self._spec_high  = spec_high
        self._spec_low   = spec_low
        self._title      = title
        self.data        = data


    def _isnumeric(data):
        if type(data) in [int, float]:
            return True
        elif type(data)==str:
            try:
                return True if (len(data.strip()) > 0 and type(float(data.strip())) == float) else False
                
            except ValueError: 
                return False
        else:
            return False

    @property
    def in_spec_data(self):
        return Statistic(list(filter(lambda x: (True if (self.spec_high==None) else (x<=self.spec_high)) and (True if (self.spec_low==None) else (x>=self.spec_low)), self._data)), parent = self)

    @property
    def trimmed_data(self):
        return Statistic(list(filter(lambda x: ( x <= self.avg + (3*self.std) ) and  (x >= self.avg - (3*self.std) ), self._data)), parent = self)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data_list):
        self._data             = data_list if type(self._parent) == Statistic else [float(data) for data in data_list if (Statistic._isnumeric(data))]
        self._parent           = None
        self._avg_not_updated  = True
        self._std_not_updated  = True
        self._max_not_updated  = True
        self._min_not_updated  = True

    @property
    def avg(self):
        if (self._avg_not_updated):
            self._avg = statistics.mean(self._data)  if len(self) > 0 else None
            self._avg_not_updated  = False
        return self._avg

    @property
    def std(self):
        if (self._std_not_updated):
            self._std = statistics.stdev(self._data) if len(self) > 0 else None
            self._std_not_updated  = False
        return self._std

    @property
    def max(self):
        if (self._max_not_updated):
            self._max = max(self._data) if len(self) > 0 else None
            self._max_not_updated  = False
        return self._max

    @property
    def min(self):
        if (self._min_not_updated):
            self._min = min(self._data) if len(self) > 0 else None
            self._min_not_updated  = False
        return self._min

    @property
    def uniformaty(self):

        return (self.max-self.min)/(2*self.avg) if not( None in [self.avg, self.max, self.min]) else None

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


    def frequency_chart(self, scale = []):
        result    = {}
        data_list = self._data
        
        if not scale:
            scale = (min(data_list), max(data_list), (max(data_list)-min(data_list))/10)

        start, stop, step = scale
        sections          = int(( stop - start ) / step)

        _ = [ result.update( { (start + (step * segment)) : 0 } )  for segment in range(sections)]

        for data in data_list:
            index = start + (step * int((data-start)/step))
            key   = list(result.keys())
            index = key[0]  if index < key[0] else ( key[-1] if index > key[-1] else index)
            result[index] += 1

        return [[float("%.12f"%key), value] for key, value in result.items()]

    @property
    def len(self):
        return len(self._data)

    def __getitem__(self, index):
        if type(index) == int:
            if index < len(self):
                return self.data[index]
            else:
                raise IndexError("data access with index %d out of range" % index)
        else:
            raise TypeError("data access with unsupported type %s " % type(index))

    def _operators(self, another, operator):
            if type(another) == Statistic:
                # print(self.data, another.data if (self.len >= another.len) else another.data, self.data)
                host_data, client_data = (self.data, another.data) if (self.len >= another.len) else (another.data, self.data)
                if (operator == "add"):
                    host_data = [data +  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]
                        
                elif (operator == "sub"):
                    host_data = [data -  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                elif (operator == "mul"):
                    host_data = [data *  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]      

                elif (operator == "div"):
                    host_data = [data /  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                elif (operator == "mod"):
                    host_data = [data %  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                elif (operator == "pow"):
                    host_data = [data ** client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                return Statistic(host_data, parent = self)

            elif (type(another) in [int, float]):

                if (operator == "add"):
                    self.data = [data +  another for data in self.data]

                elif (operator == "sub"):
                    self.data = [data -  another for data in self.data]

                elif (operator == "mul"):
                    self.data = [data *  another for data in self.data]

                elif (operator == "div"):
                    self.data = [data /  another for data in self.data]

                elif (operator == "mod"):
                    self.data = [data %  another for data in self.data]

                elif (operator == "pow"):
                    self.data = [data ** another for data in self.data]

                return self
            else:
                raise TypeError("__%s__ operation on %s to %s is not supported" % (operator, type(self), type(another)))
        


    def __add__(self, another):
        return self._operators(another, "add")

    def __iadd__(self, another):
        return self.__add__(another)

    def __radd__(self, another):
        return self.__add__(another)

    def __sub__(self, another):
        return self._operators(another, "sub")

    def __isub__(self, another):
        return self.__sub__(another)

    def __rsub__(self, another):
        return self.__sub__(another)

    def __mul__(self, another):
        return self._operators(another, "mul")

    def __imul__(self, another):
        return self.__mul__(another)

    def __rmul__(self, another):
        return self.__mul__(another)

    def __truediv__(self, another):
        return self._operators(another, "div")

    def __idiv__(self, another):
        return self.__truediv__(another)

    def __mod__(self, another):
        return self._operators(another, "mod")

    def __imod__(self, another):
        return self.__mod__(another)

    def __pow__(self, another):
        return self._operators(another, "pow")

    def __ipow__(self, another):
        return self.__pow__(another)

    def __neg__(self):
        self.data = [data * -1 for data in self.data]
        return self        

    def __abs__(self):
        self.data = [abs(data) for data in self.data]
        return self

    def __int__(self):
        self.data = [int(data) for data in self.data]
        return self

    def __float__(self):
        return self

    def __len__(self):
        return len(self._data)

    def __str__(self):
        std_p3s = None if None in [self.avg, self.std] else (self.avg + (3*self.std))
        std_m3s = None if None in [self.avg, self.std] else (self.avg - (3*self.std))

        return u"""
title: %s
 +3s : %s
 avg : %s
 -3s : %s
 std : %s
 max : %s
 min : %s
  U%% : %s
 USL : %s
 LSL : %s
 len : %s
""" % (self.title, std_p3s, self.avg, std_m3s, self.std, self.max, self.min, self.uniformaty, self.spec_high, self.spec_low, self.len)


class File(object):
    file_types = (("csv files","*.csv"),("txt files","*.txt"),("all files","*.*"))
    def __init__(self):
        self._cache = cache

    def open_file_dialog():
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(initialdir = File._load_cache(),title = "Select file", filetypes = File.file_types)
        File._set_cache(path)
        return path

    def open_path_dialog():
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(initialdir = File._load_cache(),title = "Select folder", filetypes = File.file_types)
        File._set_cache(path)
        return path


    def save_file_dialog():
        root = Tk()
        root.withdraw()        
        path =  tkFileDialog.asksaveasfilename(initialdir = File._load_cache(),title = "Select file", filetypes = File.file_types)
        File._set_cache(path)
        return path


    def _load_cache():
        path = "/path.cache"
        file = Path(path)
        if file.exists():
            with open(path,'r') as file:
                try:
                    return file.read()
                except:
                    return "/"
        else:
            return "/"

    def _set_cache(data):
        path = "/path.cache"
        file = Path(path)
        with open(path,'w') as file:
            file.write(data)


if __name__ == '__main__':

    # file_name = "C:/Users/rawr/Downloads/MOCK_DATA.csv"
    file_name = File.open_file_dialog()
    # file_list = Parse.file_in_path("C:/Users/rawr/Downloads/")
    # result_a  = Parse.multiple_csv(file_list, 0, [3])

    # Parse.print(Parse.csv(file_name)[:20])

    reslut_b  =  Parse.list_translate(Parse.csv(file_name, 1, [4, 5, 6, 7]))
    
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
    v00 = Statistic(reslut_b[0][:20], spec_high=1.2, spec_low=.8).in_spec_data 
    v11 = Statistic(reslut_b[1][:20], spec_high=1.2, spec_low=.8).in_spec_data 
    print(v00.data)
    print(v11.data)
    print((v00+v11).data)

