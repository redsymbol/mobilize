'''
Utilities used by tests in this project
'''

import os
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def data_file_path(*components):
    '''
    path to test data file
    '''
    parts = [os.path.dirname(__file__), 'data'] + list(components)
    return os.path.join(*parts)

def normxml(s):
    '''
    normalize an XML string for relaxed comparison
    '''
    return ''.join(line.strip() for line in s.split('\n'))
