import numpy as np
import pandas as pd

np.random.seed(42)

N = 520  # at least 500 records

first_names_m = ["Aarav","Vihaan","Vivaan","Ansh","Krishna","Ishaan","Rohan","Aditya","Kabir","Arjun",
                  "Rahul","Sahil","Aman","Karan","Yash","Dev","Nikhil","Varun","Siddharth","Manav"]
first_names_f = ["Ananya","Diya","Ira","Myra","Sara","Aadhya","Kiara","Riya","Isha","Priya",
                  "Neha","Pooja","Sneha","Tanya","Meera","Anika","Kavya","Trisha","Bhavya","Shreya"]
last_names = ["Sharma","Verma","Gupta","Reddy","Iyer","Nair","Menon","Rao","Patel","Singh",
              "Kumar","Das","Chatterjee","Mukherjee","Joshi","Malhotra","Kapoor","Bhat","Pillai","Naidu"]

departments = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil"]
subjects_by_dept = {
    "Computer Science": ["Data Structures", "Operating Systems", "DBMS", "Computer Networks", "Machine Learning"],
    "Information Technology": ["Web Technology", "Cloud Computing", "DBMS", "Software Engineering", "Cyber Security"],
    "Electronics": ["Digital Electronics", "Signals & Systems", "Microprocessors", "VLSI Design", "Control Systems"],
    "Mechanical": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "Manufacturing Tech", "Robotics"],
    "Civil": ["Structural Analysis", "Surveying", "Concrete Technology", "Geotechnical Eng", "Transportation Eng"],
}
semesters = [1,2,3,4,5,6,7,8]

rows = []
sid_counter = 1001

n_students = 130
students = []
for i in range(n_students):
    gender = np.random.choice(["Male","Female"])
    name = f"{np.random.choice(first_names_m if gender=='Male' else first_names_f)} {np.random.choice(last_names)}"
    dept = np.random.choice(departments)
    sem = int(np.random.choice(semesters))
    students.append({
        "student_id": f"STU{sid_counter}",
        "name": name,
        "gender": gender,
        "department": dept,
        "semester": sem
    })
    sid_counter += 1

for stu in students:
    subs = subjects_by_dept[stu["department"]]
    n_subs = np.random.randint(3,5)
    chosen_subs = np.random.choice(subs, size=min(n_subs, len(subs)), replace=False)
    for subject in chosen_subs:
        study_hours = round(np.clip(np.random.normal(4.5, 2.0), 0.5, 12), 1)
        attendance = round(np.clip(np.random.normal(78, 14), 40, 100), 1)

        base_ability = np.clip(np.random.normal(65, 15), 20, 100)
        ability = 0.5*base_ability + 0.3*(study_hours/12*100) + 0.2*attendance
        noise = np.random.normal(0, 6)
        perf = np.clip(ability + noise, 0, 100)

        assignment = round(np.clip(perf/100*20 + np.random.normal(0,1.5), 0, 20), 1)
        quiz = round(np.clip(perf/100*10 + np.random.normal(0,1), 0, 10), 1)
        lab = round(np.clip(perf/100*20 + np.random.normal(0,1.5), 0, 20), 1)
        internal = round(np.clip(perf/100*20 + np.random.normal(0,1.5), 0, 20), 1)
        previous_sem = round(np.clip(perf/100*100 + np.random.normal(0,5), 0, 100), 1)
        project = round(np.clip(perf/100*10 + np.random.normal(0,1), 0, 10), 1)
        final_exam = round(np.clip(perf/100*50 + np.random.normal(0,4), 0, 50), 1)

        total = round(assignment + quiz + lab + internal*0 + project + final_exam, 1)
        max_total = 20+10+20+10+50
        percentage = round(total/max_total*100, 2)

        if percentage >= 90: grade = "A+"
        elif percentage >= 80: grade = "A"
        elif percentage >= 70: grade = "B+"
        elif percentage >= 60: grade = "B"
        elif percentage >= 50: grade = "C"
        elif percentage >= 40: grade = "D"
        else: grade = "F"

        pass_fail = "Pass" if (percentage >= 40 and final_exam >= 15) else "Fail"

        rows.append({
            "Student_ID": stu["student_id"],
            "Student_Name": stu["name"],
            "Gender": stu["gender"],
            "Department": stu["department"],
            "Semester": stu["semester"],
            "Subject": subject,
            "Attendance": attendance,
            "Study_Hours": study_hours,
            "Assignment_Marks": assignment,
            "Quiz_Marks": quiz,
            "Lab_Marks": lab,
            "Internal_Marks": internal,
            "Previous_Semester_Marks": previous_sem,
            "Project_Marks": project,
            "Final_Exam_Marks": final_exam,
            "Total": total,
            "Percentage": percentage,
            "Grade": grade,
            "Pass_Fail": pass_fail
        })

df = pd.DataFrame(rows)
if len(df) < 500:
    extra_needed = 500 - len(df)
    df = pd.concat([df, df.sample(extra_needed, replace=True, random_state=1)], ignore_index=True)

df.to_csv("dataset/student_dataset.csv", index=False)
print("Rows generated:", len(df))
print(df.head())
print(df['Pass_Fail'].value_counts())
