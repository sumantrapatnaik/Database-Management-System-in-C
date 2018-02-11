import subprocess, datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

query_1 = '''SELECT employee_id, first_name, middle_name, last_name, home_phone
FROM employee
END'''

emp_data = {}
process = subprocess.run('./database', input=query_1.encode('UTF-8'), stdout=subprocess.PIPE)
for line in process.stdout.decode('utf-8').strip().split('\n'):
    values = line.split(',')
    emp_id = values[0]
    emp_data[emp_id] = {
        'employee_id': values[0],
        'first_name': values[1],
        'middle_name': values[2],
        'last_name': values[3],
        'home_phone': values[4],
        'shifts': {
        }
    }

query_2 = '''SELECT employee_id, date_of_shift, shift_timing, dept_name, role_name
FROM  schedule, employee, shift, department, roles
WHERE schedule_employee_id  = employee_id
AND  schedule_shift_id = shift_id
AND  schedule_dept_id = dept_id
AND roles = role_id
AND  schedule_week_no = "2"
END'''

process = subprocess.run('./database', input=query_2.encode('UTF-8'), stdout=subprocess.PIPE)
for line in process.stdout.decode('utf-8').strip().split('\n'):
    values = line.split(',')
    emp_id = values[0]

    shift = {
        'dept_name': values[3],
        'role_name': values[4]
    }

    if values[2] not in emp_data[emp_id]['shifts']:
        emp_data[emp_id]['shifts'][values[2]] = {
            '0': False,
            '1': False,
            '2': False,
            '3': False,
            '4': False,
            '5': False,
            '6': False
        }

    month, day, year = (int(x) for x in values[1].split('/'))
    weekday = str(datetime.date(year, month, day).weekday())
    emp_data[emp_id]['shifts'][values[2]][weekday] = shift

with open('report-1.html', 'w') as report:
    template = env.get_template('report-1.html')
    report.write(template.render(employees=emp_data))

#print(emp_data)

query_3 = '''SELECT dept_name, date_of_shift, shift_timing, role_name, number_needed
FROM department, schedule, shift, needs, roles
WHERE schedule_dept_id = dept_id
AND schedule_shift_id = shift_id
AND schedule_need_id = need_id
AND need_role_id = role_id
AND schedule_week_no = "2"
END'''

dept_needs = {}
process = subprocess.run('./database', input=query_3.encode('UTF-8'), stdout=subprocess.PIPE)
for line in process.stdout.decode('utf-8').strip().split('\n'):
    values = line.split(',')
    dept_name = values[0]
    need = {
        'time': values[2],
        'role': values[3],
        'number': values[4]
    }

    if dept_name not in dept_needs:
        dept_needs[dept_name] = {
            '0': [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': []
        }
    
    month, day, year = (int(x) for x in values[1].split('/'))
    weekday = str(datetime.date(year, month, day).weekday())
    dept_needs[dept_name][weekday].append(need)

with open('report-2.html', 'w') as report:
    template = env.get_template('report-2.html')
    report.write(template.render(dept_needs=dept_needs))

query_4 = '''SELECT dept_name, date_of_shift, shift_timing, employee_id, first_name, middle_name, last_name, home_phone
FROM department, schedule, employee, shift
WHERE schedule_dept_id = dept_id
AND schedule_shift_id = shift_id
AND schedule_employee_id = employee_id
AND schedule_week_no = "2"
END'''

emp_schedule= {}
process = subprocess.run('./database', input=query_4.encode('UTF-8'), stdout=subprocess.PIPE)
for line in process.stdout.decode('utf-8').strip().split('\n'):
    values = line.split(',')
    emp_id = values[3]

    if emp_id not in emp_schedule:
        emp_schedule[emp_id] = {
            '0': [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': []
        }

    month, day, year = (int(x) for x in values[1].split('/'))
    weekday = str(datetime.date(year, month, day).weekday())

    emp_schedule[emp_id][weekday].append({
        'time': values[2],
        'dept': values[0],
    })

with open('report-3.html', 'w') as report:
    template = env.get_template('report-3.html')
    report.write(template.render(emp_data=emp_data, emp_schedule=emp_schedule))

query_5 = '''SELECT dept_name, date_of_shift, shift_timing, salary
FROM department, schedule, employee, shift
WHERE schedule_dept_id = dept_id
AND schedule_shift_id = shift_id
AND schedule_employee_id = employee_id
AND schedule_week_no = "2"
END'''

dept_shifts = {}
process = subprocess.run('./database', input=query_5.encode('UTF-8'), stdout=subprocess.PIPE)
for line in process.stdout.decode('utf-8').strip().split('\n'):
    values = line.split(',')
    dept_name = values[0]

    if dept_name not in dept_shifts:
        dept_shifts[dept_name] = 0
    
    dept_shifts[dept_name] += int(values[3])

with open('report-4.html', 'w') as report:
    template = env.get_template('report-4.html')
    report.write(template.render(dept_cost=dept_shifts))