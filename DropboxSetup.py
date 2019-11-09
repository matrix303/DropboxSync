"""
A module to write or read a Dropbox Access Token file.
Based heavily on a module of the same name by Michelle
Gill (mlgill).

The Dropbox API v2 now uses an Access Token insteaad of the
previous App Token and App Secret. To get an Access Token
you must go to the Dropbox API v2 website at

https://www.dropbox.com/developers

If you are doing this for use by Synchronator in Pythonista
then follow these steps. (It is recommended that you do them
on the iOS device where you will be running Pythonista so that
you can easily copy the Access Token and paste it into the
Pythonista prompt when needed.)

1. Create an app that uses the Dropbox API.
2. Select the App Folder option.
3. Give your app a name. I recommend Synchronator-<your name>.
    The app name you choose MUST be unique.

If the previous steps were successful then you have created
an app and are now on a page where you can edit the properties
for your app.

4. Find the property "Generated Access Token" and select
the Generate button.
5. Select and copy the Access Token to the clipboard.
6. Execute Synchronator in Pythonista on your iOS device.
7. Enter the Access Token at the prompt. (Copy and paste is
ideal so you do not make a mistake. )

If everything was done properly then Synchronator will attempt
to synchronize your Pythonista files to Dropbox.

There are many different applications that can take advantage
of Dropbox, that is why this module has been kept seperate
from any applications.

Usage:
To read an existing token:

import DropboxSetup
dbx = DropboxSetup.init('<TOKEN_FILENAME>')

To write a new token:

import DropboxSetup
dbx = DropboxSetup.init('<TOKEN_FILENAME>', '<ACCESS_TOKEN>')
"""

import bs4
import dropbox
import importlib
import os
import platform
import plistlib
import requests
import sys



PYPI_MAP = {
    'bs4'       : 'beautifulsoup4',
    'dateutil'  : 'py-dateutil',
    'faker'     : 'Faker',
    'sqlite3'   : 'pysqlite',
    'yaml'      : 'PyYAML',
    'xhtml2pdf' : 'pisa',
    'Crypto'    : 'pycrypto',
    'PIL'       : 'Pillow'
}

try:
    raw_input          # Python 2
except NameError:
    raw_input = input  # Python 3


def __get_module_version(in_module_name):
    try:
        mod = importlib.import_module(in_module_name)
        fmt = "### hasattr({}, '{}')".format(in_module_name, '{}')
        for attr_name in ['__version__', 'version', '__VERSION__', 'PILLOW_VERSION', 'VERSION']:
            if in_module_name == 'markdown' and attr_name == '__version__':
                continue
            if in_module_name == 'reportlab':
                attr_name = 'Version'
            if hasattr(mod, attr_name):
                if attr_name != '__version__':
                    print(fmt.format(attr_name))
                the_attr = getattr(mod, attr_name)
                return str(the_attr() if callable(the_attr) else the_attr)
        return '?' * 5
    except:
        return 'Not Found'



def __get_module_version_from_pypi(module_name='bs4'):
    module_name = PYPI_MAP.get(module_name, module_name)
    url = 'https://pypi.python.org/pypi/{}'.format(module_name)
    soup = bs4.BeautifulSoup(requests.get(url).content, 'html5lib')
    tag = soup.find("h1", class_="package-header__name")
    if tag is None:
        return 'Not Found'
    vers_str = tag.string.split()[-1]
    if vers_str == 'Packages':
        return soup.find('div', class_='section').a.string.split()[-1]
    return vers_str


def __test_dropbox_version():
    v = __get_module_version("dropbox")
    if v != '?????':
        vp = v.split('.')
        if len(vp) >= 1:
            mjv = int(vp[0])
            if mjv > 7: return True
            if len(vp) >= 2 and mjv == 7:
                mnv = int(vp[1])
                if mnv > 2: return True
                if len(vp) >= 3 and mnv == 2:
                    dbv = int(vp[2])
                    if dbv >= 1:
                        return True
    print("DropboxSetup requires package dropbox version 7.2.1 or later!")
    return False


def __read_token(token_filepath):
    with open(token_filepath, "rt") as in_file:
        return in_file.read()


def __write_token(token_filepath, access_token):
    with open(token_filepath, 'wt') as out_file:
        out_file.write(access_token)


def check_dependencies(modules):
    print('```')  # start the output with a markdown literal

    fmt = '| {:<13} | {:<11} | {:<11} | {}'
    div = fmt.format('-' * 13, '-' * 11, '-' * 11, '')
    print(fmt.format('module', 'local', 'PyPI', ''))
    print(fmt.format('name', 'version', 'version', ''))
    print(div)
    for module_name in modules:
        local_version = __get_module_version(module_name)
        pypi_version = __get_module_version_from_pypi(module_name)
        if '?' in local_version or '$' in local_version:
            advise = local_version
        else:
            advise = '' if local_version == pypi_version else 'Upgrade?'
        print(fmt.format(module_name, local_version, pypi_version, advise))
    print(div)
    print('```')  # end of markdown literal


def init(token_filename, access_token=None, token_directory='.Tokens'):
    """
    Configure and open a Dropbox connection.

    string -- token_filename
    string -- access_token (default None)
    string -- token_directory (default 'Tokens')
    """
    # if not __test_dropbox_version():
    #     return None
    token_directory = token_directory or ''
    token_directory = os.path.abspath(token_directory)
    if not os.path.exists(token_directory):
        os.mkdir(token_directory)
    token_filepath = os.path.join(token_directory, token_filename)
    if access_token is None:
        if os.path.exists(token_filepath):
            access_token = __read_token(token_filepath)
        else:
            return None
    else:
        if os.path.exists(token_filepath):
            os.remove(token_filepath)
        __write_token(token_filepath, access_token)
    dbx = dropbox.Dropbox(access_token)
    return dbx


def get_access_token():
    """
    Prompt for and get the access token.
    This method is provided so that a consistent prompt is always used.
    """
    return raw_input('Enter access token:').strip()


def get_token_filename():
    """
    Prompt for and get the token filename.
    This method is provided so that a consistent prompt is always used.
    """
    return raw_input('Enter token filename:').strip()
