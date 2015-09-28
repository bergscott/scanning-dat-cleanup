FILENAME = 'vbextrct.dat'
NAME_START = 40
NAME_END = 58
NAME_LEN = NAME_END - NAME_START + 1
ANSWERS_START = 90
ANSWERS_END = 289
ANSWERS_LEN = ANSWERS_END - ANSWERS_START + 1

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
    
    
        


    
