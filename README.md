# All might 2d data processer

### Introduction
------
<h5>Parse module static methods:</h5>

```python
unit(data_str, out_fmt = "%.3e", if_error = None)

... data_str = "12.34keV"
... Parse.unit(data_str)
>>> "1.234e4" #output will remove postfix 'eV'

... data_str = "abc"
... Parse.unit(data_str)
>>> None #error relpacement value can be specified by 'if_error' parameter
```



```python
csv(file_path, start_row = 0, columns = [], delimiters = "[,]+", translate = False)
'''
example data: "./customer_info.txt"
    
	0	customer	sex		age		VIP
    1	    Bill	 M		25		 Y
    2	   Steve	 M		20		 Y
    3	    Jack	 M		17		 Y
    4       Rick	 M		22		 N
    5     Sophie	 F		41		 Y
    6       Jill	 F		28		 N
'''

... file_name = "./customer_info.txt"
... Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"]) #columns is optional, default will parse all the data.
>>> [
    	["customer", "age"],
    	[    "Bill",  "25"],
	    [   "Steve",  "20"],
    	[    "Jack",  "17"],
    	[    "Rick",  "22"],
    	[  "Sophie",  "41"],
    	[    "Jill",  "28"]
	]

... Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"], translate = True)
>>> [
    	["customer", "Bill", "Steve", "Jack", "Rick", "Sophie", "Jill"], 
    	[     "age",   "25",    "20",   "17",   "22",     "41",   "28"]
	]
    
```



```python
multiple_csv(file_list, start_row = 0, columns = [], delimiters = "[,]+")
```



```python
list_translate(data_list)
```



```python
file_in_path(folder_path, post_fix = "csv")
```



