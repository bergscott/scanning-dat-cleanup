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
        representing a bubble scan sheet with attributes, NAME (last name) and
        ANSWERS (200 question responses)
        line: str (from ScanTools .dat file (length = 291))
        """
        self.name = line[NAME_START:NAME_END+1].rstrip()
        self.answers = line[ANSWERS_START:ANSWERS_END+1]

    def get_name(self):
        return self.name

    def set_name(self, name):
        if len(name) <= NAME_LEN:
            self.name = name
        else:
            raise ValueError('NAME must be no greater than ' + str(NAME_LEN) +\
                    ' characters long.')

    def get_answers(self, name):
        return self.answers
    
    def set_answer(self, qNum, ans):
        """
        Sets the answer to question number QNUM to ANS and updates self.answers
        qNum: int
        ans: str or int in [1, 2, 3, 4, 5, '1', '2', '3', '4', '5', ' ']
        """
        assert ans in [1,2,3,4,5,'1','2','3','4','5', ' ']
        self.answers = self.answers[:qNum-1] + str(ans) + self.answers[qNum:]

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
        result = ' '*NAME_START
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
            raise ValueError("DATE not valid date string in form 'MMDDYYYY'")

    def get_course(self):
        return self.course
    
    def set_course(self, course):
        """
        Sets self.course to COURSE
        course: int or str
        """
        if 999 < int(course) < 100000:
            self.course = str(course).strip()
        else:
            raise ValueError('COURSE must be 4 or 5 digit number')

    def get_examLength(self):
        return self.examLength

    def set_examLength(self, length):
        """
        Sets self.examLength to LENGTH
        length: an int [0-200]
        """
        if 0 <= length <= 200:
            self.examLength = length
        else:
            raise ValueError('LENGTH must be within [0-100]')

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
        astQuests = []
        for i in xrange(len(answers)):
            if answers[i] == '*':
                astQuests.append(i)
        return astQuests

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
        result = ' '*NAME_START
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
        datFile = open(filename, 'r')
        self.key = AnswerKey(datFile.readline())
        self.responses = []
        for line in datFile:
            if len(line) == LINE_LENGTH:
                self.responses.append(StudentResponse(line))
        datFile.close()
        
    def get_key(self):
        return self.key

    def get_responses(self):
        return self.responses

    def __iter__(self):
        for sheet in [self.key] + self.responses:
            yield sheet
            
    def write_file(self, filename='test.dat', overwrite=True):
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
        newFile = open(filename, 'w')
        for sheet in self:
            newFile.write(sheet.assemble())
        newFile.close()

def load_exam(filename='vbextrct.dat'):
    return ScannedExam(filename)

def test():
    exam = load_exam()
    key = exam.get_key()
    resp = exam.get_responses()
    key.set_date('10082015')
    key.print_status()
    exam.write_file(filename='test.dat', overwrite=False)

######## Old Functions to Port to OOP Model ########
def clean_line_ends(questions):
    oldfile = open(FILENAME, 'r')
    lines = oldfile.readlines()
    oldfile.close()
    toadd = ''
    for c in xrange(ANSWERS_LEN - questions):
        toadd += ' '
    toadd += '\n'
    newlines = ''
    for l in lines:
        if len(l) == LINE_LENGTH:
            newlines += l[:ANSWERS_START+questions] + toadd
    newfile = open(FILENAME, 'w')
    newfile.write(newlines)
    newfile.close()

def prompt_change(filename):
    while True:
        choice = raw_input('Choose key attribute to change (1-7, q to quit): ')
        if choice == '1':
            name = raw_input('Enter new name: ').upper()
            change_name(filename, name)
        if choice == '2':
            numQ = int(raw_input('Enter new number of questions: '))
            change_num_questions(filename, numQ)
        if choice == '3':
            courseNum = raw_input('Enter new course number: ')
            change_course_num(filename, courseNum)
        if choice == '4':
            date = raw_input('Enter new date (MMDDYYYY)')
            change_date(filename, date)
        if choice == '5':
            choice = raw_input('Add key indicator (y/n)?: ').lower()
            if choice == 'y':
                add_key_indicator(filename)
            if choice == 'n':
                pass
            else:
                print 'Invalid choice!'
        if choice == '6':
            choice = raw_input('Clean end of key (y/n)?: ').lower()
            if choice == 'y':
                clean_key_end(filename)
            if choice == 'n':
                pass
            else:
                print 'Invalid choice!'
        if choice == '7':
            replace_asterisks(filename)
        if choice in ['q', 'Q']:
            break
        else:
            print 'Invalid choice!'
