from flask import Flask, render_template, request, session
import sqlite3 as sql
import speech_recognition as sr 
import os
import webbrowser
import pyttsx3

#add os.system('pip install libraryName') for all library imports
#add system talking back to student when processing requests
#system should introduce itself act as advisor
dirname = os.path.dirname(__file__)
app = Flask(__name__, template_folder = os.path.join(dirname,'pages'))
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
import pyttsx3
url = "http://127.0.0.1:5000"
webbrowser.open_new_tab(url)
def SpeakText(command):
     
    # Initialize the engine
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    engine.setProperty('voice', voices[1].id)

    engine.say(command)
    engine.runAndWait()


def speak():
    # get audio from the microphone                                                                       
    r = sr.Recognizer()                                                                                   

    with sr.Microphone() as source:                                                                       
        #SpeakText("Please chose an option:")                                                                                   
        audio1 = r.listen(source, timeout = 3, phrase_time_limit = 3)   

    audio = r.recognize_google(audio1)
    return audio

def current_GPA():
    points = 0
    grade_c = {"A":4,"A-":3.67
               ,"B+":3.33,"B":3.0
               ,"B-":2.67, "C+":2.33
               ,"C":2.0,"C-":1.67
               ,"D+":1.33,"D":1.0
               ,"F":0}
    studentID = session['username']
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT StudentID, Grade FROM Grades WHERE StudentID = ?', (studentID,))
        con.commit
    Student = cur.fetchall()   
    length = len(Student)
    grades = []
    for x in range(length):
        grades.append(Student[x][1])
    print(grades)
    for grade in grades:
        points += grade_c[grade]
    gpa = points / len(grades)
    print(gpa)
    return gpa

def transcript():
    studentID = session['username']
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT StudentID, CourseName, CourseNumber, Credits FROM Past_Enrollments WHERE StudentID = ?', (studentID,))
        con.commit
    Student = cur.fetchall()
    return Student


def catalog():
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT CourseID, Course_Name, Credits, Professor FROM Courses')
        con.commit
    courses = cur.fetchall()
    return courses

def course_Information(Course_Name):
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Courses WHERE Course_Name = ?', Course_Name)
        con.commit
    courses = cur.fetchall()
    if courses == None:
        courses = "There is no course with that ID"
        return courses
    else:
        return courses

def what_if_GPA(what_if_grades):
    points = 0
    grade_c = {"A":4.0,"A-":3.67
               ,"B+":3.33,"B":3.0
               ,"B-":2.67, "C+":2.33
               ,"C":2.0,"C-":1.67
               ,"D+":1.33,"D":1.0
               ,"F":0}
    studentID = session['username']
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT StudentID, Grade FROM Grades WHERE StudentID = ?', (studentID,))
        con.commit
    Student = cur.fetchall()   
    length = len(Student)
    grades = []
    i = 0
    for x in range(length):
        grades.append(Student[x][1])
    while i < len(what_if_grades):
        grades.append(what_if_grades[i])
        i+=1
    print(grades)
    for grade in grades:
        points += grade_c[grade]
    gpa = points / len(grades)
    print(gpa)
    return gpa

def Fcourses(courses):
    finalcourselist =[] 
    for ID in courses: 
        if int(ID[0]) < 200:
            finalcourselist.append(ID) 
    return finalcourselist
    
def Scourses(courses):
    finalcourselist =[] 
    for ID in courses: 
        if int(ID[0]) > 200 and int(ID[0]) <300:
            finalcourselist.append(ID) 
    return finalcourselist

def Jcourses(courses):
    finalcourselist =[] 
    for ID in courses: 
        if int(ID[0]) > 300 and int(ID[0]) <400:
            finalcourselist.append(ID) 
    return finalcourselist

def Secourses(courses):
    finalcourselist =[] 
    for ID in courses: 
        if int(ID[0]) > 400:
            finalcourselist.append(ID) 
    return finalcourselist

def filtercourses(courses):
    studentID = session['username']
    with sql.connect("Advising.db") as con:
        cur = con.cursor()
        cur.execute('SELECT CourseID FROM Grades WHERE StudentID = ?', (studentID,))
        con.commit
    courseids = cur.fetchall() 
    print("this is it",courseids[0][0])
    i = 0
    j = 0

    while i < len(courses):
            while j < len(courseids):
                 if int(courses[i][0]) == int(courseids[j][0]):
                    courses.pop(i) 
                 j = j +1   
            i = i +1 
            j = 0
    return courses

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/home', methods = ['POST'])
def loginVerification():
    if request.method == 'POST':
        ID = request.form['ID']
        password = request.form['password']
        with sql.connect("Advising.db") as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM Students WHERE StudentID = ? AND password = ?', (ID, password,))
            con.commit
        Student = cur.fetchone()
        if Student == None:
            return render_template('login.html')
        department = Student[5]
        minor = Student[7]
        if department == 'CS' or department == 'IT' or minor == 'IT' or minor == 'CS':
            if Student[1] == ID:
                firstName = Student[3]
                lastName = Student[4]
                session['username'] = ID
                question = 'Please vocally state which module you want'
                SpeakText("Hello welcome to our new system")

                return render_template('home.html', question=question, firstName=firstName, lastName = lastName)
            else:
                return render_template('login.html')
        else :
            SpeakText("Sorry currently this system is only for Computer science and Information Technology department")                                                                                   
            return render_template('login.html')


@app.route('/speak', methods = ['POST'])
def speakHomeModule():
    home = "1. home"
    q2 = "2. State the full course name you want information on (ex. Robotics)"
    if request.method == 'POST':
        value = request.form['button']

    if value == '1':
        audio = speak()
        print("you said", audio)
        
        if "transcript" in audio:
            trans = transcript()
            statement = "This is your unofficial transcript"
            return render_template('transcript.html', trans=trans, statement=statement)   

        elif "current GPA" in audio:
            gpa = current_GPA()
            return render_template("GPA.html", gpa=gpa, home=home)

        elif "what if GPA" in audio:
            what_if_statement = "Please state how many grades you want to enter"
            statement_whatif = "Please then state your what-if grade point in a numerical format from the list (A = 4.0...)"
            return render_template("GPA2.html", what_if_statement=what_if_statement, statement_whatif=statement_whatif, home=home)

        elif "catalog" in audio:
            courses = catalog()
            statement = "This is the full course catalog"
            return render_template('catalog.html', courses=courses, statement=statement, home=home, q2=q2)
        elif "advisement" in audio:
            courses = catalog()
            statement = "This is the full course catalog"
            courses = filtercourses(courses)
            
            if session ['year'] == "freshmen":
                currentsemester = Fcourses(courses)
                nextsemester = Scourses(courses)
            elif session ['year'] == "sophomores":
                currentsemester = Scourses(courses)
                nextsemester = Jcourses(courses)
            elif session ['year'] == "juniors":
                currentsemester = Jcourses(courses)
                nextsemester = Secourses(courses)
            elif session ['year'] == "seniors":
                currentsemester = Secourses(courses)
                return render_template('advising1.html', courses=courses, statement=statement, home=home, currentsemester=currentsemester)

            return render_template('advising.html', courses=courses, statement=statement, home=home, nextsemester=nextsemester ,currentsemester=currentsemester)

        elif "home" in audio:
            return render_template('home.html')

        elif "end session" in audio:
            return render_template('login.html')

        else:
            question = 'you didnt say a choice, please make sure to say a choice'
            return render_template('home.html', question=question)


    if value == '2':
        audio = speak()
        print("you said", audio)
        if "home" in audio:
            return render_template('home.html')   
        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('GPA.html', statement=statement, home=home)


    if value == '3':
        audio = speak()
        print("you said", audio)
        if "home" in audio:
            return render_template('home.html')   
        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('transcript.html', statement=statement) 

    if value == '4':
        with sql.connect("Advising.db") as con:
            cur = con.cursor()
            cur.execute('SELECT Course_Name FROM Courses')
            con.commit
        courses = cur.fetchall()


        audio = speak()
        audio = audio.lower()
        course_select = (audio,)
        print("you said", audio)
        print(course_select)
        x = 0

        if "home" in audio:
            return render_template('home.html')

        elif course_select in courses:
            while x < len(courses):
                if course_select == courses[x]:
                    print(courses[x])
                    course_info = course_Information(courses[x])
                    x +=1
                    break
                else:
                    x +=1

            return render_template('catalog.html', course_info=course_info, home=home) #needs to be worked on

        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('catalog.html', statement=statement, home=home)

    if value == '5':
        audio = speak()
        print("you said", audio)
        number = audio
        if "home" in audio:
                return render_template('home.html') 
        number = int(number)
        grades = []
        k = 0
        while k < number:
            print("Talk")
            #implement text to speech to state to enter the grade in a numerical float format from the list of grade points up in the defined function current_GPA
            audio = speak()
            print("you said", audio)
            if audio == '4.0':
                temp = "A"
                grades.append(temp)
            elif audio == '3.67':
                temp = "A-"
                grades.append(temp)
            elif audio == '3.33':
                temp = "B+"
                grades.append(temp)
            elif audio == '3.0':
                temp = "B"
                grades.append(temp)
            elif audio == '2.67':
                temp = "B-"
                grades.append(temp)
            elif audio == '2.33':
                temp = "C+"
                grades.append(temp)
            elif audio == '2.0':
                temp = "C"
                grades.append(temp)
            elif audio == '1.67':
                temp = "C-"
                grades.append(temp)
            elif audio == '1.33':
                temp = "D+"
                grades.append(temp)
            elif audio == '1.0':
                temp = "D"
                grades.append(temp)
            elif audio == '0.0':
                temp = "F"
                grades.append(temp)
            else:
                SpeakText("Grade point is not accepted, please try again")
                #text to speech that, the grade point is not accepted, please try again
                k=k

            k += 1
        #grades = [float(j) for j in grades]
        print(grades)
        final_what_if = what_if_GPA(grades)

        if "home" in audio:
            return render_template('GPA2.html') 
        elif  final_what_if != None:
            statement = "this is your what-if GPA"
            return render_template('GPA2.html', statement=statement, home=home, final_what_if=final_what_if) 
        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('GPA2.html', statement=statement, home=home) 

    if value == '6':
        audio = speak()
        print("you said", audio)
        courses = catalog()
        statement = "This is the full course catalog"
        courses = filtercourses(courses)
        if session ['year'] == "freshmen":
                currentsemester = Fcourses(courses)
                nextsemester = Scourses(courses)
        elif session ['year'] == "sophomores":
                currentsemester = Scourses(courses)
                nextsemester = Jcourses(courses)
        elif session ['year'] == "juniors":
                currentsemester = Jcourses(courses)
                nextsemester = Secourses(courses)
        elif session ['year'] == "seniors":
                currentsemester = Secourses(courses)   
        if "home" in audio:
            return render_template('home.html')   
        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('advising.html', courses=courses, statement=statement, home=home, nextsemester=nextsemester ,currentsemester=currentsemester)
    if value == '7':
        audio = speak()
        print("you said", audio)
        courses = catalog()
        statement = "This is the full course catalog"
        courses = filtercourses(courses)
        if session ['year'] == "freshmen":
                currentsemester = Fcourses(courses)
                nextsemester = Scourses(courses)
        elif session ['year'] == "sophomores":
                currentsemester = Scourses(courses)
                nextsemester = Jcourses(courses)
        elif session ['year'] == "juniors":
                currentsemester = Jcourses(courses)
                nextsemester = Secourses(courses)
        elif session ['year'] == "seniors":
                currentsemester = Secourses(courses)        
        if "home" in audio:
            return render_template('home.html')   
        else:
            statement = 'You didnt say a choice, please make sure to say a choice'
            return render_template('advising1.html', courses=courses, statement=statement, home=home, currentsemester=currentsemester)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)


