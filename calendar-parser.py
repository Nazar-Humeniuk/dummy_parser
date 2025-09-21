import os
import csv
import json
from collections import defaultdict

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
    """Parse employee holiday/sick leave information."""
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
    """Convert day abbreviations in employees to 'dd.mm.YYYY' format."""
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
                employees[employee][day_type][idx] = f"{d.zfill(2)}.{m_num}.{year}"

    return employees

def save_json(employees: dict, save_path, save_folder="results"):
    """Save employees data to a JSON file."""
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    file_name = save_path.split('/')
    file_name = file_name[len(file_name)-1].split('.')[0]
    with open("results/"+file_name+".json", mode='w', encoding='utf-8') as json_file:
        json.dump(employees, json_file, indent=4)

def execution():
    # requirements
    path = "files/" # path to your csv file or to folder
    year = [] # year of calendar

    # optional
    approved_holiday    = True
    sick_leave          = True
    special_leave       = True
    national_holiday    = False

    # save paramenters
    is_save = True
    save_folder = "results"

    # save data
    all_employees_data = {}

    if not (path):
        raise ReferenceError("Missing required arguments: path")
    try:
        csv_files = []
        if os.path.isdir(path):
            csv_files = [path+'/'+f for f in os.listdir(path) if os.path.isfile(path+'/'+f) and
                            f.endswith('csv')]
            year = [file.split('/')[-1].split('_')[0] for file in csv_files]
        elif os.path.isfile(path) and path.endswith("csv"):
            csv_files.append(path)
            year.append(csv_files[0].split('/')[1].split('_')[0])
        else:
            raise ValueError("Wrong file or directory format!")
        for index, csv_file in enumerate(csv_files):
            calendar_data = open_csv_calendar(csv_file)
            date_start_row, date_start_column = find_Date(calendar_data)
            employee_start_row = date_start_row + 2
            days = parse_days(calendar_data, start_row_index=date_start_row, start_column_index=date_start_column)
            employees = parse_employees(
                calendar_data,
                start_row_index=employee_start_row,
                days_start_index=date_start_column,
                approved_holiday=approved_holiday,
                sick_leave=sick_leave,
                special_leave=special_leave,
                national_holiday=national_holiday
            )

            employees = convert_dates(employees, days, year[index])

            if is_save:
                save_json(employees, save_path=csv_file, save_folder=save_folder)

            # uncomment if you are going to use this code to working with data farther
            # all_employees_data[year[index]] = employees
        # return all_employees_data
    except ReferenceError:
        pass
    except ValueError:
        pass

# ----------------------
# Main execution
# ----------------------
if __name__ == "__main__":
    execution()
