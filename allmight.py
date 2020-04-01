#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import glob
import math
import os.path
import statistics

from pathlib         import Path
from tkinter         import Tk, filedialog
from scipy.optimize  import curve_fit

try:
    import cPickle as pickle
except:
    import pickle

try:
    import numpy   as np
except :
    pass



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

    def csv(file_path, start_stop_row = [], columns = [], delimiters = "[,]+", translate = False):
        result         = []
        tresult        = []
        column_counter = []
        start_row      = -1
        stop_row       = float("inf")  

        if not os.path.isfile(file_path):
            raise FileExistsError()

        split_regex = ("[%s]+" % "".join(set(delimiters))) if isinstance(delimiters, (list, tuple, set)) else delimiters

        with open(file_path, encoding="utf-8") as file:

            if (type(start_stop_row) == int):
                start_row = start_stop_row
            elif start_stop_row==[]:                
                start_row = 0
            elif type(start_stop_row) == list and len(start_stop_row)==2:
                start_row, stop_row = start_stop_row
            else:
                raise TypeError("Parse.csv dose not support paramater with %s type or %s value" % (type(start_stop_row), start_stop_row) )

            for row, line in enumerate(file):
                if row >= start_row and row <= stop_row:
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
        self._sum        = None
        self._avg        = None
        self._std        = None
        self._uniformaty = None
        self._outlier    = None
        self._yield_rate = None
        self._ca         = None
        self._cp         = None
        self._cpk        = None
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


    def in_spec_data(self):
        return Statistic(list(filter(lambda x: (True if (self.spec_high==None) else (x<=self.spec_high)) and (True if (self.spec_low==None) else (x>=self.spec_low)), self._data)), parent = self)


    def trimmed_data(self, sigma = 3):
        return Statistic(list(filter(lambda x: ( x <= self.avg + (sigma*self.std) ) and  (x >= self.avg - (sigma*self.std) ), self._data)), parent = self)


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
        self._set_not_updated()

    def _set_not_updated(self):
        self._parent            = None
        self._avg_not_updated   = True
        self._std_not_updated   = True
        self._max_not_updated   = True
        self._min_not_updated   = True
        self._sum_not_updated   = True
        self._yield_not_updated = True
        self._ca_not_updated    = True
        self._cp_not_updated    = True
        self._cpk_not_updated   = True

    def append(self, data):
        if (type(data) in [int, float]) or (type(data) == str and Statistic._isnumeric(data)):
            self._data.append(float(data))
        elif type(data) == Statistic:
            self |= data
        elif  type(data) == list:
            self |= Statistic(data)
        else:
            raise TypeError ("append unsupported type {0}: {0}" % (type(data), data))

    def pop(self, index):
        self._set_not_updated()
        return self._data.pop(index)

    def remove(self, index):
        self._set_not_updated()
        return self._data.remove(index)
    
    @property
    def sum(self):        
        if (self._sum_not_updated):
            self._sum = math.fsum(self._data)
            self._sum_not_updated  = False
        return self._sum

    @property
    def avg(self):
        if (self._avg_not_updated):
            self._avg = self.sum/self.len if self.len > 0 else None
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

    @property
    def yield_rate(self):
        if not (None in [self.spec_high, self.spec_low]):
            if (self._yield_not_updated):
                self._yield_rate = sum(  (1 if (data <= self.spec_high) and (data >= self.spec_low) else 0) for data in self._data) / len(self)
                self._sum_not_updated  = False
            return self._yield_rate
        return None

    @property
    def ca(self):
        if not (None in [self.spec_high, self.spec_low]):
            if (self._ca_not_updated):
                self._ca = (((self.spec_high + self.spec_low) / 2.0) - self.avg) / (self.spec_high - self.spec_low)
                self._ca_not_updated = False
            return self._ca
        return None
            
    @property
    def cp(self):
        if not (None in [self.spec_high, self.spec_low]):
            if (self._cp_not_updated):
                self._cp = (self.spec_high - self.spec_low) / (6 * self.std)
                self._cp_not_updated = False
            return self._cp
        return None
    
    @property
    def cpk(self):
        if not (None in [self.spec_high, self.spec_low]):
            if (self._cpk_not_updated):
                self._cpk = (1 - self.ca) * self.cp
                self._cpk_not_updated = False
            return self._cpk
        return None          

    def frequency_chart(self, scale = [], display = False):
        result    = {}
        data_list = self._data
        
        if not scale:
            scale = (min(data_list), max(data_list), (max(data_list)-min(data_list))/10)

        start, stop, step = scale
        sections          = int(( stop - start ) / step)


        _ = [ result.update( { (start + (step * segment)) : 0 } )  for segment in range(sections + 1)]

        for data in data_list:
            index = start + (step * int((data-start)/step))
            key   = list(result.keys())
            index = key[0]  if index < key[0] else ( key[-1] if index > key[-1] else index)
            result[index] += 1
        
        if display:
            template = ""
            for key, value in result.items():
                template += ("{:.8f} : {:d}\n".format(key, value))
            return template

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
        elif type(index) == slice:
            return Statistic([self[i] for i in range(*index.indices(len(self)))], parent = self)
        else:
            raise TypeError("data access with unsupported type %s " % type(index))

    def _operators(self, another, operator, mode = None):
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

                elif (operator == "and"):
                    host_data = [data for data in self.data if data in another.data ]

                elif (operator == "or"):
                    host_data =  self.data + another.data

                elif (operator == "xor"):
                    host_data =  [data for data in (self.data + another.data) if not (data in (self.data or another.data))  ]

                elif (operator == "mod"):
                    host_data = [data %  client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                elif (operator == "pow"):
                    host_data = [data ** client_data[i] if i < len(client_data) else data for i, data in enumerate(host_data) ]

                if mode == "i":
                    self._data = host_data
                    self._set_not_updated()
                    return self

                return Statistic(host_data, parent = self)

            elif (type(another) in [int, float]):

                if (operator == "add"):
                    self._data = [data +  another for data in self.data]

                elif (operator == "sub"):
                    self._data = [data -  another for data in self.data]

                elif (operator == "mul"):
                    self._data = [data *  another for data in self.data]

                elif (operator == "div"):
                    self._data = [data /  another for data in self.data]

                elif (operator == "mod"):
                    self._data = [data %  another for data in self.data]

                elif (operator == "pow"):
                    self._data = [data ** another for data in self.data]

                else:
                    raise TypeError("__%s__ operation on %s to %s is not supported" % (operator, type(self), type(another)))

                self._set_not_updated()
                return self
            else:
                raise TypeError("__%s__ operation on %s to %s is not supported" % (operator, type(self), type(another)))
        


    def __add__(self, another):
        return self._operators(another, "add")

    def __iadd__(self, another):
        return self._operators(another, "add", mode = "i")

    def __radd__(self, another):
        return self.__add__(another)

    def __sub__(self, another):
        return self._operators(another, "sub")

    def __isub__(self, another):
        return self._operators(another, "sub", mode = "i")

    def __rsub__(self, another):
        return self.__sub__(another)

    def __mul__(self, another):
        return self._operators(another, "mul")

    def __imul__(self, another):
        return self._operators(another, "mul", mode = "i")

    def __rmul__(self, another):
        return self.__mul__(another)

    def __truediv__(self, another):
        return self._operators(another, "div")

    def __idiv__(self, another):
        return self._operators(another, "div", mode = "i")

    def __and__(self, another):
        return self._operators(another, "and")

    def __iand__(self, another):
        return self._operators(another, "and", mode = "i")

    def __or__(self, another):
        print("K")
        return self._operators(another, "or")

    def __ior__(self, another):
        return self._operators(another, "or", mode = "i")

    def __mod__(self, another):
        return self._operators(another, "mod")

    def __imod__(self, another):
        return self._operators(another, "mod", mode = "i")

    def __pow__(self, another):
        return self._operators(another, "pow")

    def __ipow__(self, another):
        return self._operators(another, "pow", mode = "i")

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

    def __repr__(self):
        return "<Statistic, title: %s, len: %s>" % (self.title, self.len)

    def __str__(self):
        tempate = ""
        avg_p6s = None if None in [self.avg, self.std] else (self.avg + (6*self.std))
        avg_p3s = None if None in [self.avg, self.std] else (self.avg + (3*self.std))
        avg_m3s = None if None in [self.avg, self.std] else (self.avg - (3*self.std))
        avg_m6s = None if None in [self.avg, self.std] else (self.avg - (6*self.std))
        items   = [   "title", "avg+6s", "avg+3s",    "avg", "avg-3s", "avg-6s", "stddev",    "max",    "min",            "U%",       "spec_H",      "spec_L",         "yield",    "sum", "length"]
        values  = [self.title,  avg_p6s,  avg_p3s, self.avg,  avg_m3s,  avg_m6s, self.std, self.max, self.min, self.uniformaty, self.spec_high, self.spec_low, self.yield_rate, self.sum, self.len]

        for index, item in enumerate(items):
            value     = values[index]
            if type(value) in [type(None), str]:
                tempate  += "{:>10} : {:}\n".format(item, value)
            elif type(value) in [float, int]:
                if (int(value)==value):
                    tempate  += "{:>10} : {:d}\n".format(item, int(value))
                else:
                    tempate  += "{:>10} : {:.8f}\n".format(item, value)

        return (tempate)

class Fitting(object):
    def __init__(self, data, parent=None):
        pass

    def fit_gaussian(x, y, mean, sigma):
        popt, pcov = curve_fit(Fitting.gauss_function, x, y, p0=[1,mean,sigma])
        return popt, pcov

    def gauss_function(x, a, x0, sigma):
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

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
    print(file_name)

    reslut  =  (Parse.csv(file_name))

    Parse.print(reslut)


