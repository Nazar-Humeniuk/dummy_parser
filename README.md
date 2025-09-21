# How to use

1. Install python if you don't have it yet
2. Pull this repository to your local machine
3. Open calendar-parser.py and set up values for next fields:
    - **path**: file name of your csv file or path to folder with file(s)
4. Run calendar-parser.py
``python calendar-parser.py``

Script will for all files with extension '.csv'.
You can collect all file in one folder or have file in the same folder as python file.

## Important!
**Script parse only csv extension files**

## The data will be in the next JSON format:

```json
{
    "employee_name" {
        "requested_holiday": "<list>",
        "national_holiday": "<list>",
        "special_leave": "<list>",
        "sick_leave": "<list>",
        "holidays": "<int>",
        "sick": "<int>",
        "special leave": "<int>",
        "national holiday": "<int>"
    }
}
```

### You can add or revome values such as:
- holidays
- sick
- special_leave
- national holiday

Set them to value __False__ in the **execution** function.

You can set folder where you want to save file by ovewriting variable **save_folder** in **execution** function.

If you don't want save data to files then ovewrite valiable **is_save** to __False__ in **execution** fucntion.

If you are going to use this code to work pass this data to database, please **uncomment** last part of execution function. Then the data will be returned as result of the function.