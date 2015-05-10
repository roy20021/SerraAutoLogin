from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [
"os",
"sys",
"configparser",
"pickle",
"traceback",
"string",
"win32api",
"win32con",
"win32gui_struct",
"win32gui", 
"re",
"threading",
"socket", 
"urllib",
"ssl",
"posixpath",
"http.server",
"requests", 
"requests.adapters",
#"requests.compat",
#'requests.packages',
#'requests.packages.chardet',
#'requests.packages.urllib3',
#'requests.packages.urllib3.exceptions',
#'requests.packages.urllib3.util',
#'requests.packages.urllib3.packages',
#'requests.packages.urllib3.contrib',
#'requests.packages.urllib3.contrib.ntlmpool',
#'requests.packages.urllib3.contrib.pyopenssl',
#'requests.packages.urllib3.packages.ssl_match_hostname',
], excludes = [], icon="icon/SerraAutoLogin.ico")#, include_files = [("C:\\cacert.pem",'cacert.pem')])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('SerraAutoLogin.py', base=base)
]

setup(name='SerraAutoLogin',
      version = '1.1.0',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
