# How to use

1. Install python if you don't have it yet
2. Pull this repository to your local machine
3. Open calendar-parser.py and set up values for next fields:
    - **file_name**: file name of your csv file
    - **year**: year of the callendar you are about to parse
4. Run calendar-parser.py
``python calendar-parser.py``

## Important!
**Script parse only csv extension files**

# The data will be in the next JSON format:

``
{
    employee_name {
        "requested_holiday": list,
        "national_holiday": list,
        "special_leave": list,
        "sick_leave": list,
        "holidays": int,
        "sick": int,
        "special leave": int,
        "national holiday": int
    }
}
``

### You can add or revome values such as:
- holidays
- sick
- special_leave
- national holiday

Set them to value False in the **main** function

