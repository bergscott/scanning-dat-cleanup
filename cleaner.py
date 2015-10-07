import datetime

FILENAME = 'vbextrct.dat'
NAME_START = 40
NAME_END = 58
NAME_LEN = NAME_END - NAME_START + 1
ANSWERS_START = 90
ANSWERS_END = 289
ANSWERS_LEN = ANSWERS_END - ANSWERS_START + 1
NUMQ_START = 76
NUMQ_END = 78
KEY_INDICATOR = 74
COURSE_NUM_START = 84
COURSE_NUM_END = 89
DATE_START = 66
DATE_END = 73
LINE_LENGTH = 291

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

def check_name(name):
    name = name.upper()
    oldfile = open(FILENAME, 'r')
    key = oldfile.readline()
    oldfile.close()
    username = key[NAME_START:NAME_END+1].rstrip()
    if username != name:
        while True:
            doFix = raw_input('Name on key does not match "' + name + \
                              '". Do you wish to change it (y/n)?: ')
            if doFix in ['y', 'Y']:
                print 'Fixing name...'
                newKey = replace_name(name, key)
                assert newKey[-1] == '\n'
                replace_key(newKey, FILENAME)
                print 'Fixed!'
                break
            if doFix in ['n', 'N']:
                print 'Leaving name as is.'
                break
            else:
                print 'Invalid input!'
    else:
        print 'Name check passed!'

def replace_name(name, key):
    newName = name + ''.join([' ' for i in xrange(NAME_LEN - len(name))])
    return key[:NAME_START] + newName + key[NAME_END+1:]

def replace_key(newKey, f):
    oldfile = open(f, 'r')
    lines = oldfile.readlines()
    oldfile.close()
    lines[0] = newKey
    newfile = open(f, 'w')
    newfile.writelines(lines)
    newfile.close()

def show_info(filename):
    datFile = open(filename, 'r')
    key = datFile.readline()
    datFile.close()
    name = key[NAME_START:NAME_END+1].rstrip()
    numQuestions = key[NUMQ_START:NUMQ_END+1]
    courseNum = key[COURSE_NUM_START:COURSE_NUM_END+1].strip()
    date = key[DATE_START:DATE_END+1]
    print '[1] Name on exam:\t\t' + name
    print '[2] Number of questions:\t' + numQuestions
    print '[3] Course number:\t\t' + courseNum
    if is_valid_date(date):
        print '[4] Date:\t\t\t' + '{}/{}/{}'.format(date[0:2], date[2:4], date[4:8])
    else:
        print '[4] Date:\t\t\tINVALID DATE!'
    if key[KEY_INDICATOR] == '1':
        print '[5] Key Indicator:\t\tok'
    else:
        print '[5] Key Indicator:\t\tINCORRECT'
    if detect_noise(key, int(numQuestions)):
        print '[6] Errant marks detected at end of key. Dark sheet?'
    else:
        print '[6] Noise check passed.'
    print '[7] ' + report_asterisks(key)
    
def detect_noise(key, numQuestions):
    for c in key[ANSWERS_START+numQuestions:ANSWERS_END+1]:
        if c != ' ':
            return True
    return False

def is_valid_date(date):
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

def asterisk_check(key):
    astQuests = []
    for i in range(ANSWERS_START, ANSWERS_END+1):
        if key[i] == '*':
            astQuests.append(i + 1 - ANSWERS_START)
    return astQuests

def report_asterisks(key):
    asterisksList = asterisk_check(key)
    if len(asterisksList) == 0:
        return 'No asterisks on key.'
    else:
        report = 'Asterisk found on question(s) '
        for q in asterisksList:
            report += str(q) + ', '
        return report[:-2]

def change_prompt(filename):
    raise NotImplementedError
