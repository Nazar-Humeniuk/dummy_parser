import os
import csv
import json
from collections import defaultdict
from datetime import datetime

def open_csv_calendar(file_name: str):
    """Open and read a CSV file into a list of rows."""
    try:
        with open(file_name, mode="r", encoding="utf-8", newline="") as file:
            return list(csv.reader(file))
    except Exception as ex:
        print(f"Error reading {file_name}: {ex}")
        return []


def find_Date(csv_data):
    """Find 'Date' in csv as reference point"""
    for row, data in enumerate(csv_data):
        if "Date" in data:
            column = data.index("Date")
            return row, column
    return None

def parse_days(csv_data, start_row_index, start_column_index):
    """Parse day headers from the CSV file."""
    if not csv_data or len(csv_data) <= start_row_index:
        return []
    return [str(col) for i, col in enumerate(csv_data[start_row_index])
            if i >= start_column_index and col]


def parse_employees(
        data,
        start_row_index,
        days_start_index,
        approved_holiday=False,
        sick_leave=False,
        special_leave=False,
        national_holiday=False
    ):
    """Parse employee holiday/sick leave etc information."""
    ATTRIBUTES = [
        "requested_holiday",
        "approved_holiday",
        "national_holiday",
        "special_leave",
        "sick_leave",
    ]

    employee_name_index = 1

    employees = defaultdict(lambda: {attr: [] for attr in ATTRIBUTES})

    for row in data[start_row_index:]:
        employee = row[employee_name_index]
        if not employee:
            continue

        for idx, cell in enumerate(row[days_start_index:]):
            match cell.lower():
                case "r": employees[employee]["requested_holiday"].append(idx)
                case "a": employees[employee]["approved_holiday"].append(idx)
                case "n": employees[employee]["national_holiday"].append(idx)
                case "s": employees[employee]["special_leave"].append(idx)
                case "z": employees[employee]["sick_leave"].append(idx)


        if approved_holiday:
            employees[employee].update({
                 "holidays": len(employees[employee]["approved_holiday"])
        })
        if sick_leave:
            employees[employee].update({
                 "sick": len(employees[employee]["sick_leave"])
        })

        if special_leave:
             employees[employee].update({
                 "special-leave": len(employees[employee]["special_leave"])
        })

        if national_holiday:
             employees[employee].update({
                 "national-holiday": len(employees[employee]["national_holiday"])
        })

    return employees

def convert_dates(employees: dict, days: list, year: str):
    """Convert day abbreviations in employees to 'YYYY-mm-dd' format."""
    MONTHS = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sept': '09', 'Sep': '09', 'Oct': '10',
        'Nov': '11', 'Dec': '12'
    }

    ATTRIBUTES = [
        "requested_holiday",
        "approved_holiday",
        "national_holiday",
        "special_leave",
        "sick_leave",
    ]

    for employee, data in employees.items():
        for day_type in ATTRIBUTES:
            for idx, day_index in enumerate(data[day_type]):
                day_str = days[day_index]
                d, m = day_str.split("-")
                m_num = MONTHS[m]
                employees[employee][day_type][idx] = f"{year}-{m_num}-{d.zfill(2)}"

    return employees

def save_json(employees: dict, save_path, save_folder="results"):
    """Save employees data to a JSON file."""
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    file_name = save_path.split('/')
    file_name = file_name[len(file_name)-1].split('.')[0]
    with open("results/"+file_name+".json", mode='w', encoding='utf-8') as json_file:
        json.dump(employees, json_file, indent=4)

def execution(sql_option=False, json_option=False):
    # requirements
    path = "files/" # path to your csv file or to folder

    # optional
    approved_holiday    = True
    sick_leave          = True
    special_leave       = True
    national_holiday    = False

    # json save paramenters
    is_json_save = json_option
    save_folder = "results"

    # csv save parameters
    is_sql_save = sql_option

    # save data objects
    all_employees_data = {}

    # list of years
    year = []

    if not (path):
        raise ReferenceError("Missing required arguments: path")
    try:
        """Save input files"""
        csv_files = []

        # if 'path' is forlder then open it and save only with extension .csv
        if os.path.isdir(path):
            csv_files = [path+'/'+f for f in os.listdir(path) if os.path.isfile(path+'/'+f) and
                            f.endswith('csv')]
            year = [file.split('/')[-1].split('_')[0] for file in csv_files]
        # if 'path' is file then save the file
        elif os.path.isfile(path) and path.endswith("csv"):
            csv_files.append(path)
            year.append(csv_files[0].split('/')[1].split('_')[0])
        else:
            raise ValueError("Wrong file or directory format!")

        """Parse input files"""
        for index, csv_file in enumerate(csv_files):
            calendar_data = open_csv_calendar(csv_file) # save all the rows
            date_start_row, date_start_column = find_Date(calendar_data) # find reference point
            employee_start_row = date_start_row + 2 # add 2 rows to be on row where first employee starts
            days = parse_days(calendar_data, start_row_index=date_start_row, start_column_index=date_start_column) # parse all of the days title (for ex. 25-Sept)
            employees = parse_employees(
                calendar_data,
                start_row_index=employee_start_row,
                days_start_index=date_start_column,
                approved_holiday=approved_holiday,
                sick_leave=sick_leave,
                special_leave=special_leave,
                national_holiday=national_holiday
            ) # parse all an emloyee days
            employees = convert_dates(employees, days, year[index]) # convert days to database format (for ex. 2025-09-25)

            # json saving option
            if is_json_save:
                save_json(employees, save_path=csv_file, save_folder=save_folder)
        # sql saving option
        if is_sql_save:
            all_employees_data[year[index]] = employees
            return all_employees_data
    except ReferenceError:
        pass
    except ValueError:
        pass

def is_weekend(date_str: str):
    """Check if 'date_str' is weekend"""
    return "FALSE" if datetime.strptime(date_str, "%Y-%m-%d").weekday() < 5 else "TRUE"

def save_sql_file(year: str, query_str: str):
    """Save builded query to .sql file"""
    try:
        with open(f"employees_data_{year}.sql", mode='w') as sql_file:
            sql_file.write(query_str)
    except Exception as ex:
        print(ex)

def build_sql_query(all_employees: dict, user_ids: dict, status_category_ids: dict):
    """Build sql query to insert all the data to database.
    As the result every row is insert to avoid conflicts and make usable
    ON CONFLICT DO NOTHING instruction"""

    # DB day types (categories)
    CATEGORIES = {
        "approved_holiday": "Approved Holiday",
        "national_holiday": "National Holiday",
        "special_leave": "Special Leave",
        "sick_leave": "Sick Leave",
        "requested_holiday": "Requested Holiday"
    }

    BASE_QUERY = 'INSERT INTO day_statuses (user_id, date, is_weekend, status_category_id) VALUES'

    for year, employees_data in all_employees.items():
        query = ""
        for employee_name, day_types in employees_data.items():
            query+=f"\n--*****{employee_name}*****\n"
            # type of days
            for day_type, days in day_types.items():
                if days and type(days) is list:
                    # parse days withing category
                    for day in days:
                        user_id_request = f"(SELECT u.id FROM users u WHERE u.name = '{employee_name}')"
                        status_category_id_request = f"(SELECT sc.id FROM status_categories sc WHERE sc.name = '{CATEGORIES[day_type]}')"
                        query+=f"{BASE_QUERY} ({user_id_request}, '{day}', {is_weekend(day)}, {status_category_id_request}) ON CONFLICT DO NOTHING;\n"

        save_sql_file(year, query_str=query)

# ----------------------
# Main execution
# ----------------------
if __name__ == "__main__":
    save_to_sql_file = True
    save_to_json_file = False
    data = execution(sql_option=save_to_sql_file, json_option=save_to_json_file)
    if save_sql_file:
        build_sql_query(all_employees=data, user_ids={}, status_category_ids={})
