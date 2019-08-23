import sys
import getopt
from bs4 import BeautifulSoup
import requests

BASE_URL = r"https://www.thesaurus.com/browse/{0}"

# dictionary src: https://www.ef.com/wwen/english-resources/english-vocabulary/top-1000-words/
DEFAULT_DICT = 'dict.txt'

def usage():
    '''Help menu.'''
    print('python[3] dumblinter.py args:')
    print('-h or --help to see this screen')
    print('-f or -file= to specify which file to parse')
    print('-d or --dict= to specify which dictionary file to use')
    print('-m or --min to specify the minimum lenght a word to be processed')
    print('Note that a valid dictionary file has one word in each line and no spaces.')
    print('ALL WORDS WILL BE MADE lower caps.')
    sys.exit()

def find_synonyms(word):
    '''Function that searches the Thesaurus for synonyms. Returns a list
       of synonyms.'''
    #format the url for the word given
    search_url = BASE_URL.format(word)

    # try the request
    try:
        result = requests.get(search_url)
    except requests.exceptions.RequestException:
        print('Failed to connect to url: ' + search_url)
        print('Status code returned: ' + result.status_code)
        print('Check your internet connection.')

    # extract content and cook it
    site = result.content
    soup = BeautifulSoup(site, 'lxml')

    # find first list
    patterns = soup.find_all('ul', class_='css-1lc0dpe et6tpn80')
    raw_block = patterns[0]

    # extract list items
    raw_items = raw_block.find_all('li')
    synonyms = []

    # get rid of the tags
    for item in raw_items:
        synonyms.append(item.get_text())
    return synonyms

def build_dictionary(dct):
    '''Takes in file name and builds a dictionary set from it.'''
    dictionary = set()
    print(dct)
    try:
        d = open(dct, 'r')
        for line in d:
            dictionary.add(line.lower())
        d.close()
    except:
        print('Something went wrong with building the dictionary.', end=' ')
        print('Make sure you follow specifications.')
        usage()
    return dictionary

def display_synonyms(lst, dictionary):
    '''Displays numbered options list.'''
    print('Note: Words in the dictionary have an x in front of the number.')
    for i, s in enumerate(lst, 1):
        if s in dictionary:
            print('x' + str(i) + ': ' + str(s), end='  ')
        else:
            print('-' + str(i) + ': ' + str(s), end='  ')
    print('\n', end='')


def parse_file(fd, dictionary, minimum=3):
    '''Takes in file descriptor and a dictionary and parses the file.
       Returns text for a new file.'''
    print(dictionary)
    new_text = ''
    for cnt, line in enumerate(fd, 1):
        print('Line ' + str(cnt) + ': ' + line)
        words = line.split()
        for word in words:
            if word.lower() not in dictionary and len(word) >= minimum:
                print("Word '" + word + "' is not in the dictionary. Finding synonyms...")
                syn = find_synonyms(word.lower())
                if len(syn) == 0:
                    print('No synonyms have been found for: ' + word + '.')
                    continue
                display_synonyms(syn, dictionary)
                while True:
                    try:
                        n = int(input('Pick a number or type 0 to pass: '))
                        if n == 0:
                            new_text += word
                            new_text += ' '
                            break
                        new_text += syn[n-1]
                        new_text += ' '
                        break
                    except:
                        print('Not a number!')
            else:
                new_text += word
                new_text += ' '
        new_text += '\n'
    return new_text

def main():
    '''Main program that gets called at launch.'''
    in_file = ''
    in_dict = ''
    in_min = 3
    # handle command line arguments
    if len(sys.argv) < 2:
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:d:m:', ['help', 'file=', 'dict=', 'min='])
    except:
        usage()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-f', '--file'):
            in_file = arg
        elif opt in ('-d', '--dict'):
            in_dict = arg
        elif opt in ('-m', '--min'):
            in_min = int(arg)
        else:
            usage()

    # handle unspecified arguments
    if in_file == '':
        print('File name is missing.')
        sys.exit()
    if in_dict == '':
        in_dict = DEFAULT_DICT

    dictionary = build_dictionary(in_dict)

    try:
        fd = open(in_file, 'r')
        new_text = parse_file(fd, dictionary, in_min)
        new_file = open('dumb.txt', 'w')
        new_file.write(new_text)
        new_file.close()
        fd.close()
    except:
        print('File does not exist!')
        sys.exit()

main()
