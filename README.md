# All might 2d data processer

#### Parse module static methods:



##### unit conversion:

```python
unit(data_str, out_fmt = "%.3e", if_error = None)

... data_str = "12.34keV"
... Parse.unit(data_str)
>>> "1.234e4" #output will remove postfix 'eV'

... data_str = "abc"
... Parse.unit(data_str)
>>> None #error relpacement value can be specified by 'if_error' parameter
```

------



##### parse csv or tab separated file :

sample data: "./cpu_info.txt"

| index |   CPU    | Core | threads | Clock  |
| :---: | :------: | :--: | :-----: | :----: |
|   0   | i7-8086K |  6   |   12    | 4.0GHz |
|   1   | i7-8700  |  6   |   12    | 3.2GHz |
|   2   | i7-8700K |  6   |   12    | 3.7GHz |
|   3   | i7-9700F |  8   |    8    | 3.0GHz |
|   4   | i7-9700K |  8   |    8    | 3.6GHz |

```python
csv(file_path, start_row = 0, columns = [], delimiters = "[,]+", translate = False)


... file_name = "./cpu_info.txt"
... Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"]) 
... #columns is optional, leave it will parse all the data
... #delimiter takes regex expression or python list, such as [" ", ",", ".", "abc"]
>>> [
    	[     "CPU", "threads"],
    	["i7-8086K",      "12"],
    	[ "i7-8700",      "12"],
    	["i7-8700K",      "12"],
    	["i7-9700F",       "8"],
    	["i7-9700K",       "8"]
	]

... Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"], translate = True)
>>> [
    	[    "CPU", "i7-8086K", "i7-8700", "i7-8700K", "i7-9700F", "i7-9700K"], 
    	["threads",       "12",      "12",       "12",        "8",        "8"]
	]

... Parse.csv(file_name, start_row = 1, delimiters = ["\t"])
... #can use start_row to remove undesired headers
>>> [
    	["i7-8086K",      "12"],
    	[ "i7-8700",      "12"],
    	["i7-8700K",      "12"],
    	["i7-9700F",       "8"],
    	["i7-9700K",       "8"]
	]
```

------



##### Search files in folder:

Sample file structure:

- [ ] Current Folder
  - [ ] cpu_info.txt
  - [ ] gpu_info.dat
  - [ ] power_supply_info.csv
  - [ ] rgb_chassie_info.csv



```python
... folder_path= "./"
... file_in_path(folder_path, post_fix = "csv")
>>> ["./power_supply_info.csv", "./rgb_chassie_info.csv"]

... file_in_path(folder_path, post_fix = ["csv", "txt", "dat"])
... #post_fix takes single string or list of string, does not support regex
>>> ["./power_supply_info.csv", "./rgb_chassie_info.csv", "./cpu_info.txt", "./gpu_info.dat"]

```

------



##### 2D list translation:

```python
list_translate(data_list)
... file_name = "./cpu_info.txt"
... Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"]) 
>>> [
    	[     "CPU", "threads"],
    	["i7-8086K",      "12"],
    	[ "i7-8700",      "12"],
    	["i7-8700K",      "12"],
    	["i7-9700F",       "8"],
    	["i7-9700K",       "8"]
	]

... Parse.list_translate(Parse.csv(file_name, columns = [1, 3], delimiters = ["\t"]))
>>> [
    	[    "CPU", "i7-8086K", "i7-8700", "i7-8700K", "i7-9700F", "i7-9700K"], 
    	["threads",       "12",      "12",       "12",        "8",        "8"]
	]
```

------



```python
multiple_csv(file_list, start_row = 0, columns = [], delimiters = "[,]+")
```



