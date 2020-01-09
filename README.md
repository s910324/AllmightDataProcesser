# All might 2d data processer

- package dependency: non, for scenario that your machine only got bare bone python.

  [TOC]
  
  

## ◆ Parse module static methods:

### ◎ unit conversion:

```python
unit(data_str, out_fmt = "%.3e", if_error = None)

... data_str = "12.34keV"
... Parse.unit(data_str)
>>> "1.234e4" #output will also remove suffix 'eV'

... data_str = "abc"
... Parse.unit(data_str)
... #error relpacement value can be specified by 'if_error' parameter
... #None returns original string
>>> "abc" 

... data_str = "abc"
... Parse.unit(data_str, if_error = "N/A")
>>> "N/A"

```

------



### ◎ parse csv or tab separated file :

sample data: "./mosfet_IV_1.txt"

| description | mosfet_IV |          |            |
| ----------: | :-------: | :------: | :--------: |
|        time | 20191231  |          |            |
|     program | IV_Curve  |          |            |
|       index |  voltage  | Current  | Resistance |
|           0 |   0 mV    |   0 uA   |    n/a     |
|           1 |  200 mV   |  800 uA  | 250.0 pOhm |
|           2 |  400 mV   |  6.4 mA  | 62.5 pOhm  |
|           3 |  600 mV   | 21.6 mA  | 27.8 pOhm  |
|           4 |  800 mV   | 51.2 mA  | 15.6 pOhm  |
|           5 |   1.0 V   | 100.0 mA | 10.0 pOhm  |
|           6 |   1.2 V   | 172.8 mA |  6.9 pOhm  |
|           7 |   1.4 V   | 274.4 mA |  5.1 pOhm  |
|           8 |   1.6 V   | 409.6 mA |  3.9 pOhm  |
|           9 |   1.8 V   | 583.2 mA |  3.1 pOhm  |

```python
csv(file_path, start_row = 0, columns = [], delimiters = "[,]+", translate = False)


... file_name = "./mosfet_IV_1.txt"
... Parse.csv(file_name, columns = [1, 2], delimiters = ["\t"]) 

... #columns is optional, leave it will parse all the data
... #delimiter takes regex expression or python list, such as [" ", ",", ".", ":"]
... #as demonstrated, it fills out row 1~3 with empty columns at the rear end.
>>> [
    	["mosfet_IV",      ""],
    	["20191231",       ""],
    	["IV_Curve",       ""],
    	["voltage", "current"],
    	[  "0 mV",     "0 uA"],
    	["200 mV",   "800 uA"],
    	["400 mv",   "6.4 mA"],
                 ⋮
    	[ "1.8 V", "583.2 mA"]
]


... Parse.csv(file_name, columns = [1, 2], delimiters = ["\t"], translate = True)
>>> [
    	["mosfet_IV", "20191231", "IV_Curve", "voltage", "0 mV", ...    "1.8 V"], 
    	[         "",         "",         "", "current", "0 uA", ... "583.2 mA"]
]


... Parse.csv(file_name, start_row = 2, delimiters = ["\t"])
... #can use start_row to remove undesired headers
>>> [
    	["voltage", "current"],
    	[  "0 mV",     "0 uA"],
    	["200 mV",   "800 uA"],
    	["400 mv",   "6.4 mA"],
                 ⋮
    	[ "1.8 V", "583.2 mA"]
]
```

------



### ◎ Search files in folder:

Sample file structure:

   [+]WAT_Folder

​		├─mosfet_IV_1.txt

​		├─mosfet_IV_2.txt

​		├─mosfet_IV_3.csv

​		├─mosfet_IV_4.dat

```python
... folder_path= "./"
... Parse.file_in_path(folder_path, suffix = "csv")
>>> ["./mosfet_IV_3.csv", ]

... Parse.file_in_path(folder_path, suffix = ["csv", "txt", "dat"])
... #suffix can be single string or list of string, does not support regex
>>> ["./mosfet_IV_1.txt", "./mosfet_IV_2.txt", "./mosfet_IV_3.csv", "./mosfet_IV_4.dat"]

```

------



### ◎ 2D list translation:

```python
list_translate(data_list)
... file_name = "./mosfet_IV_1.txt"
... Parse.csv(file_name, columns = [1, 2], delimiters = ["\t"]) 
>>> [
    	["mosfet_IV",      ""],
    	["20191231",       ""],
    	["IV_Curve",       ""],
    	["voltage", "current"],
    	[  "0 mV",     "0 uA"],
    	["200 mV",   "800 uA"],
    	["400 mv",   "6.4 mA"],
                  ⋮
    	[ "1.8 V", "583.2 mA"]
]


... Parse.list_translate(Parse.csv(file_name, columns = [1, 2], delimiters = ["\t"]))
>>> [
    	["mosfet_IV", "20191231", "IV_Curve", "voltage", "0 mV", ...    "1.8 V"], 
    	[         "",         "",         "", "current", "0 uA", ... "583.2 mA"]
]
```

------



### ◎ Parse and combine multiple column from different csv:

```python
... file_list = Parse.file_in_path(folder_path, suffix = ["csv", "txt", "dat"])
... print(file_list)
>>> ["./mosfet_IV_1.txt", "./mosfet_IV_2.txt", "./mosfet_IV_3.csv", "./mosfet_IV_4.dat"]

... Parse.multiple_csv(file_list, start_row = 2, columns = [2], delimiters = "[,]+")
... #parses all column 2 from every file (with same dimension) and combine them into list
... #add file name at first row as header
>>> [

    	["mosfet_IV_1", "mosfet_IV_2", ..., "mosfet_IV_4"],
    	[    "current",     "current", ...,     "current"],
    	[       "0 uA",                ...,              ],
    	[     "800 uA",                ...,              ],
    	[     "6.4 mA",                ...,              ],
                              ⋮
    	[   "583.2 mA"                              ...  ],
]


```

------



### ◎ 2D Data grid output:

```python

... Parse.print(data_list, show_index = True, pretty = true, delimiter=", ")
... # "pretty" adds blanks to aligh all column
... # "show index" add additional column that labeled each row with index
>>>  0,	  0 mV,		0 uA
    1,	200 mV,	  800 uA
    2,	400 mV,	  6.4 mA
    3,	600 mV,	 21.6 mA
    4,	800 mV,	 51.2 mA
          ⋮
    9,	 1.8 V,	583.2 mA
	


```

------



## ◆ Statistic module :

### ◎ input data and basic function:

```python
... # only support 1D data, can parse throuth dirty data, any numeric like element
... # will be treated as number and any un-parsable will be excluded.
... data = [39.082, 6.908, 14.54, 17.134, 22.95, ... , 9.552, 24.05]


... # print function shows pre-set statistical values 
... stat = Statistic(data, title = "random data")
... print(stat)
>>> title: random data
     +3s : 23.508354109740537
     avg : 15.154301158301159
     -3s : 6.800248206861781
     std : 2.7846843171464597
      U% : 0.32776173233690803
     USL : None
     LSL : None
        
        
... # aquire statistical data by attributes
... print(len(stat), stat.avg, stat.std)
>>> 30, 15.154301158301159, 2.7846843171464597 


... print(stat.max, stat.min, stat.uniformaty, stat.spec_h, stat.spec_l)
>>> 19.962, 10.028, 0.32776173233690803, None, None        

```

------



### ◎ filtering data using 'spec' attribute:

```python

```

