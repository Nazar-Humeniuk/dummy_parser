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


def parse_employees(data, start_row_index, days_start_index):
    """Parse employee holiday/sick leave information."""
    ATTRIBUTES = [
        "requested_holiday",
        "approved_holiday",
        "national_holiday",
        "special_leave",
        "sick_leave",
    ]

    employee_name_index = 1
    hdays_index = 2
    sick_index = 3

    employees = defaultdict(lambda: {attr: [] for attr in ATTRIBUTES})

    for row in data[start_row_index:]:
        employee = row[employee_name_index]
        if not employee:
            continue

        employees[employee].update({
            "hdays": row[hdays_index],
            "sick": row[sick_index],
        })

        for idx, cell in enumerate(row[days_start_index:]):
            match cell.lower():
                case "r": employees[employee]["requested_holiday"].append(idx)
                case "a": employees[employee]["approved_holiday"].append(idx)
                case "n": employees[employee]["national_holiday"].append(idx)
                case "s": employees[employee]["special_leave"].append(idx)
                case "z": employees[employee]["sick_leave"].append(idx)

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

def save_json(employees: dict, file_name="employees_data.json"):
    """Save employees data to a JSON file."""
    with open(file_name, mode='w', encoding='utf-8') as json_file:
        json.dump(employees, json_file, indent=4)

# ----------------------
# Main execution
# ----------------------
if __name__ == "__main__":
    calendar_data = open_csv_calendar("2022_MPO_Holiday_Planner.csv")
    date_start_row, date_start_column = find_Date(calendar_data)
    employee_start_row = date_start_row + 2
   # print(employee_start_row)
    # print(calendar_data)
    days = parse_days(calendar_data, start_row_index=date_start_row, start_column_index=date_start_column)
    #print(days)
    employees = parse_employees(calendar_data, start_row_index=employee_start_row, days_start_index=date_start_column)
    employees = convert_dates(employees, days, "2022")
    save_json(employees)
