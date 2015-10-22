import datetime

FILENAME = 'vbextrct.dat'
NAME_START = 40
NAME_END = 58
NAME_LEN = NAME_END - NAME_START + 1
FIRST_NAME_START = 59
FIRST_NAME_END = 64
FIRST_NAME_LEN = FIRST_NAME_END - FIRST_NAME_START + 1
ANSWERS_START = 90
ANSWERS_END = 289
ANSWERS_LEN = ANSWERS_END - ANSWERS_START + 1
NUMQ_START = 76
NUMQ_END = 78
NUMQ_LEN = NUMQ_END - NUMQ_START + 1
KEY_INDICATOR = 74
COURSE_NUM_START = 84
COURSE_NUM_END = 89
COURSE_NUM_LEN = COURSE_NUM_END - COURSE_NUM_START + 1
DATE_START = 66
DATE_END = 73
ID_START = 74
ID_END = 82
LINE_LENGTH = 291

class ScannedSheet(object):
    def __init__(self, line):
        """
        Creates an instance of the ScannedSheet class from line in a .dat file, 
        representing a bubble scan sheet with attributes:
        HEADER (bookeeping string created by ScanTools)
        NAME (last name or user ID)
        ANSWERS (200 question responses)
        line: str (from ScanTools .dat file (length = 291))
        """
        self.header = line[:NAME_START]
        self.name = line[NAME_START:NAME_END+1].rstrip()
        self.answers = line[ANSWERS_START:ANSWERS_END+1]

    def get_name(self):
        """
        Returns last name field of scanned sheet
        returns: str
        """
        return self.name

    def set_name(self, name):
        """
        Checks to see if NAME exceeds maximum length then sets the last name
        field of scanned sheet. Raises ValueError if maximum length is exceeded.
        name: str
        mutates: self.name
        """
        if len(name) <= NAME_LEN:
            self.name = name.upper()
        else:
            raise ValueError('NAME must be no greater than ' + str(NAME_LEN) +\
                    ' characters long.')

    def get_answers(self):
        return self.answers
    
    def set_answer(self, qNum, ans):
        """
        Sets the answer to question number QNUM to ANS and updates self.answers
        qNum: int
        ans: str or int in [1, 2, 3, 4, 5, '1', '2', '3', '4', '5', ' ']
        mutates: self.answers
        """
        if not ans in [1,2,3,4,5,'1','2','3','4','5', ' ']:
            try:
                ans = self.convert_answer(ans)
            except ValueError:
                raise ValueError('New answer must be number 1-5 or letter A-E.')
        self.answers = self.answers[:qNum-1] + str(ans) + self.answers[qNum:]

    def convert_answer(self, ans):
        """
        If ans is 'A', 'B', 'C', 'D', or 'E', returns '1', '2', '3', '4', or '5'
        respectively, otherwise raises ValueError. Ignores case.
        ans: str
        returns: str
        """
        convertDict = {'A':'1', 'B':'2', 'C':'3', 'D':'4', 'E':'5'}
        try:
            return convertDict[ans.upper()]
        except (KeyError, AttributeError):
            raise ValueError('Can only convert letters A-E or a-e')

    def assemble(self):
        raise NotImplementedError

class StudentResponse(ScannedSheet):
    def __init__(self, line):
        """
        Creates an instance of the StudentResponse class from line in a
        .dat file, representing a bubble scan sheet of a student's response
        with attributes:
        NAME (last name)
        FIRSTNAME (first name) 
        ANSWERS (200 question responses)
        ID (last nine digits of student ID number) 
        line: str (from ScanTools .dat file (length = 291))
        """
        ScannedSheet.__init__(self, line)
        self.id = line[ID_START:ID_END+1]
        self.firstName = line[FIRST_NAME_START:FIRST_NAME_END+1].rstrip()

    def get_id(self):
        return self.id
    
    def get_firstName(self):
        return self.firstName

    def assemble(self):
        """
        Returns a string conversion of the attributes of the
        StudentResponse instance for writing to data file.  Format of string
        is consistent with output of ScanTools program.
        returns: str
        """
        result = self.header
        result += self.name + ' '*(NAME_LEN - len(self.name))
        result += self.firstName + ' '*(FIRST_NAME_LEN - len(self.firstName))
        result += ' '*(ID_START - FIRST_NAME_END - 1)
        result += self.id
        result += ' '*(ANSWERS_START - ID_END -  1)
        result += self.answers
        result += '\n'
        assert len(result) == LINE_LENGTH
        return result

class AnswerKey(ScannedSheet):
    def __init__(self, line):
        """
        Creates an instance of the AnswerKey class from line in a .dat file,
        representing an instructor's answer key bubble scan sheet with
        attributes:
        NAME (userID)
        ANSWERS (200 question answers)
        DATE (date exam administered)
        COURSE (4 or 5 digit course number)
        EXAMLENGTH (number of questions on exam)
        KEYINDICATED (True if '1' was bubbled in column A on sheet to denote
        sheet is key, otherwise False)
        line: str (from ScanTools .dat file (length = 291))
        """
        ScannedSheet.__init__(self, line)
        self.date = line[DATE_START:DATE_END+1]
        self.course = line[COURSE_NUM_START:COURSE_NUM_END+1].strip()
        try:
            self.examLength = int(line[NUMQ_START:NUMQ_END+1])
            assert self.examLength <= ANSWERS_LEN
        except (ValueError, AssertionError):
            self.examLength = None
        self.keyIndicated = line[74] == '1'

    def get_date(self):
        return self.date

    def set_date(self, date):
        """
        Sets self.date to DATE if DATE is a valid date in form MMDDYYYY,
        otherwise raises ValueError
        date: str
        """
        if type(date) == str and len(date) == 8 and self.is_valid_date(date):
            self.date = date
        else:
            raise ValueError("DATE must be valid date in form 'MMDDYYYY'")

    def get_course(self):
        return self.course
    
    def set_course(self, course):
        """
        Sets self.course to COURSE
        course: int or str
        """
        errormsg = 'COURSE must be 4 or 5 digit number'
        try:
            if 999 < int(course) < 100000:
                self.course = str(course).strip()
            else:
                raise ValueError(errormsg)
        except ValueError:
            raise ValueError(errormsg)

    def get_examLength(self):
        return self.examLength

    def set_examLength(self, length):
        """
        Sets self.examLength to LENGTH
        length: an int [0-200]
        """
        maxExamLength = 200
        errormsg = 'Exam length must be within [0-' + str(maxExamLength) + ']'
        try:
            numQuestions = int(length)
        except ValueError:
            raise ValueError(errormsg)
        if 0 <= numQuestions <= maxExamLength:
            self.examLength = numQuestions
        else:
            raise ValueError(errormsg)

    def is_valid_date(self, date):
        """
        Checks date string in form MMDDYYYY to see if it is a valid date or all
        blank space.
        If valid or blank space, returns True, otherwise False.
        date: a str
        returns: bool
        """
        # check date string for all blank spaces or improper format
        allBlank = True
        for c in date:
            if allBlank and c != ' ':
                allBlank = False
            if not allBlank:
                if c in [' ', '*']:
                    return False
        if allBlank: return True
        # if complete date string, check if valid date
        try:
            datetime.date(int(date[4:8]), int(date[0:2]), int(date[2:4]))
            return True
        except ValueError:
            return False

    def noise_detected(self):
        """
        Returns True if any character in self.answers after the first
        self.examLength characters is not ' ', otherwise returns false.
        returns: bool
        """
        for c in self.answers[self.examLength:]:
            if c != ' ':
                return True
        return False

    def find_asterisks(self, answers):
        """
        Returns a list of indexes where answers[i] == '*'.  If no asterisks in
        answers, returns []
        answers: a str
        returns: a list of int
        """
        asterList = []
        for i in xrange(len(answers)):
            if answers[i] == '*':
                asterList.append(i)
        return asterList

    def report_asterisks(self):
        """
        Returns a string representation of the question numbers on the key
        that were scanned as asterisks (*), denoting a scanning error.
        Returns: a str
        """
        asterisksList = self.find_asterisks(self.answers)
        if len(asterisksList) == 0:
            return 'No asterisks on key.'
        else:
            report = 'Asterisk found on question(s) '
            for elem in asterisksList:
                report += str(elem+1) + ', '
            return report[:-2]

    def replace_asterisks(self, asterList):
        """
        Prompts user for new answer for each answer on key that is an asterisk.
        Replaces the asterisk with the input.
        asterList: a list of int (list of asterisk indexes from 
                   self.find_asterisks)
        mutates: self.answers
        """
        if asterList == []:
            print 'No asterisks to replace.'
        for index in asterList:
            qNum = index + 1
            while True:
                newAns = raw_input('Enter the new answer for question ' + \
                                   str(qNum) + \
                                   ' (or "S" to Skip, "Q" to quit): ').upper()
                if newAns == "S":
                    break
                elif newAns == "Q":
                    return None
                else:
                    try:
                        self.set_answer(qNum, newAns)
                        break
                    except AssertionError:
                        print 'Invalid replacement answer. Try again.'

    def clear_end(self, examLength):
        """
        For all characters in self.answers beyond examLength, replaces existing
        value with ' '.
        examLength: int (number of questions on exam)
        mutates: self.answers
        """
        cleanEnd = ' ' * (ANSWERS_LEN - examLength)
        self.answers = self.answers[:examLength] + cleanEnd
        
    def print_status(self):
        """
        Prints a string representation of an answer key, reporting any
        potential errors

        returns: str
        """
        toPrint = '[1] Name on exam:\t\t' + self.name
        toPrint += '\n[2] Number of questions:\t' + str(self.examLength)
        toPrint += '\n[3] Course number:\t\t' + self.course
        if self.is_valid_date(self.date):
            toPrint += '\n[4] Date:\t\t\t' + \
                    '{}/{}/{}'.format(self.date[0:2], self.date[2:4], \
                                      self.date[4:8])
        else:
            toPrint += '\n[4] Date:\t\t\tINVALID DATE!'
        if self.keyIndicated:
            toPrint += '\n[5] Key Indicator:\t\tok'
        else:
            toPrint += '\n[5] Key Indicator:\t\tNOT PRESENT'
        if self.noise_detected():
            toPrint += '\n[6] Errant marks detected at end of key. Dark sheet?'
        else:
            toPrint += '\n[6] Noise check passed.'
        toPrint += '\n[7] ' + self.report_asterisks()
        print toPrint

    def assemble(self):
        """
        Returns a string conversion of the attributes of the
        StudentResponse instance for writing to data file.  Format of string
        is consistent with output of ScanTools program.
        returns: str
        """
        result = self.header
        result += self.name + ' '*(NAME_LEN - len(self.name))
        result += ' '*(DATE_START - NAME_END - 1)
        result += self.date
        result += '1 '
        result += '0'*(NUMQ_LEN - len(str(self.examLength))) +\
                str(self.examLength)
        result += ' '*(COURSE_NUM_START - NUMQ_END - 1)
        result += self.course + ' '*(COURSE_NUM_LEN - len(self.course))
        result += self.answers
        result += '\n'
        assert len(result) == LINE_LENGTH
        return result

class ScannedExam(object):
    def __init__(self, filename):
        """
        Creates an instance of the ScannedExam class representing an answer key
        and group of student response sheets scanned together. Derives
        attributes from ScanTools data file at location FILENAME.
        ATTRIBUTES:
        key: AnswerKey
        responses: list of StudentResponse
        
        filename: str
        """
        datFile = open(filename, 'r')
        self.key = AnswerKey(datFile.readline())
        self.responses = []
        for line in datFile:
            if len(line) == LINE_LENGTH:
                self.responses.append(StudentResponse(line))
        datFile.close()
        
    def get_key(self):
        """
        Returns self.key (the answer key of the scanned exam)
        returns: AnswerKey
        """
        return self.key

    def get_responses(self):
        """
        Returns self.responses (a list of the student response sheets)
        returns: list of StudentResponse
        """
        return self.responses

    def __iter__(self):
        """
        Creates generator object that iteratively yields self.key then each
        member of self.responses.  Analogous to yielding one line of the 
        scanned data file at a time.

        yields: AnswerKey or StudentResponse
        """
        for sheet in [self.key] + self.responses:
            yield sheet
            
    def write_file(self, filename='vbextrct.dat', overwrite=True):
        """
        Writes key and responses to data file, FILENAME. Calls ASSEMBLE methods
        of ScannedSheet subclasses to convert ScannedSheet attributes to string.
        If OVERWRITE is False, checks to see if file of FILENAME exists.  If it
        exists, prompts the user to confirm overwrite before proceeding.

        filename: str
        overwrite: boolean
        """
        if not overwrite:
            try:
                f = open(filename)
                while True:
                    choice = raw_input('File exists, overwrite (y/n)?: ').lower()
                    if choice == 'n':
                        f.close()
                        return None
                    elif choice == 'y':
                        f.close()
                        break
                    else:
                        print 'Invalid choice!'
            except IOError:
                pass
        toWrite = ''
        for sheet in self:
            toWrite += sheet.assemble()
        newFile = open(filename, 'w')
        newFile.write(toWrite)
        newFile.close()

    def prompt_change(self):
        """
        Displays exam attributes and presents options to user for changes.
        Modifies attributes based on user's input.
        """
        prompt = 'Choose key attribute to change ' + \
                 '(1-7, "W" to write, "Q" to quit): '
        while True:
            print #blank line
            self.key.print_status()
            print #blank line
            choice = raw_input(prompt).upper()
            print #blank line
            try:
                if choice == '1':
                    name = raw_input('Enter new name: ')
                    self.key.set_name(name)
                elif choice == '2':
                    numQ = raw_input('Enter new number of questions: ')
                    self.key.set_examLength(numQ)
                elif choice == '3':
                    courseNum = raw_input('Enter new course number: ')
                    self.key.set_course(courseNum)
                elif choice == '4':
                    date = raw_input('Enter new date (MMDDYYYY): ')
                    self.key.set_date(date)
                elif choice == '5':
                    print 'Key Indicator is automatically added on write.'
                elif choice == '6':
                    choice = raw_input('Clean end of key (y/n)?: ').lower()
                    if choice == 'y':
                        self.key.clear_end(self.key.get_examLength())
                    elif choice == 'n':
                        pass
                    else:
                        raise ValueError('Invalid choice!')
                elif choice == '7':
                    self.key.replace_asterisks(self.key.find_asterisks(
                                               self.key.get_answers()))
                elif choice == 'W':
                    fname = 'test.dat'
                    print 'Writing to "' + fname + '"...'
                    self.write_file(filename=fname)
                    print 'File written!'
                    break
                elif choice == 'Q':
                    print 'Qutting without write...'
                    break
                else:
                    raise ValueError('Invalid choice!')
            except ValueError as err:
                print 'Error: ' + str(err)
                raw_input('Press ENTER to continue.')
            except IOError as err:
                print 'Error: Unable to write file - ' + str(err)
                raw_input('Press ENTER to continue.')
            else: 
                raw_input('Success! Press ENTER to continue.')

def load_exam(filename='vbextrct.dat'):
    """
    Loads an exam data file at FILENAME into a ScannedExam object, displays
    its relevant attributes to the user and prompts for action.
    filename: str
    """
    exam = ScannedExam(filename)
    exam.prompt_change()

def test():
    exam = load_exam()
    key = exam.get_key()
    resp = exam.get_responses()
    key.set_date('10082015')
    key.print_status()
    exam.write_file(filename='test.dat', overwrite=False)
    exam.prompt_change()
    
if __name__ == '__main__':
    print # blank line
    print '----------------------------------------------------------'
    print '  Welcome to Exam Data File Cleaner v0.2.1 by Scott Berg  '
    print '----------------------------------------------------------'
    while True:
        print # blank line
        choice = raw_input('Enter "L" to load exam, "Q" to quit: ').upper()
        if choice == 'L':
            exam = ScannedExam('vbextrct.dat')
            exam.prompt_change()
        elif choice == "Q":
            break
        else:
            print 'Invalid entry!'
    print # blank line
    print 'Goodbye!'
