# chi_io

Pure Python read/write encryption/decryption of encrypted Tombo chi files. If you are looking for an easy to use with safe and sane defaults for encryption do NOT use this (there a more modern and better best-practices available since 2004), this is intended to be **compatible** with [Tombo](http://tombo.osdn.jp/En/), Kumagusu, MiniNoteViewer, etc.

https://github.com/clach04/chi_io

Extracted from https://hg.sr.ht/~clach04/pytombo

Library originally supported Python 2.1, 2.2, 2.4, 2.4, 2.5, 2.6, 2.7. Now only targets Python 2.7 and 3.x. Use older version shipped with PyTombo for Python < 2.7.


  * [Getting Started](#getting-started)
  * [Examples](#examples)
    + [Python code](#python-code)
      - [In memory](#in-memory)
      - [Using filenames](#using-filenames)
  * [Tests](#tests)
  * [NOTES](#notes)
  * [Also see](#also-see)
  * [TODO](#todo)


## Getting Started

Assuming a local checkout:

    python -m pip install -r requirements.txt  # runs faster Py2 and Py3, slower alternative is `python -m pip install blowfish` Python 3 only

    python test_chi.py

## Examples


### Command line tool chi_io

    echo test | env CHI_PASSWORD=test ./chi_tool.py  -e -s  | env CHI_PASSWORD=test ./chi_tool.py -s -v

    echo test | ./chi_tool.py -p test -e -s  | ./chi_tool.py -p test -s -v

    mkdir scratch
    echo my data | python chi_tool.py -p test -e -o scratch/mynote.chi
    echo test > scratch/password
    od -c scratch/password
    ./chi_tool.py scratch/mynote.chi -P scratch/password


### Python code

#### In memory

Using https://peps.python.org/pep-0272/ **like** API

    Python 3.10.4 (tags/v3.10.4:9d38120, Mar 23 2022, 23:13:41) [MSC v.1929 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import chi_io  # https://github.com/clach04/chi_io Python access to Tombo encrypted files
    >>> chi_io.implementation
    'using PyCrypto 3.17'
    >>> plain_text = b'12345678'
    >>> mypassword = b'testing'
    >>> cipher = chi_io.PEP272LikeCipher(chi_io.CHI_cipher(mypassword))  # OPTIONAL! encryption and decryption will be faster on subsequent calls if the same password
     is used
    >>> crypted_data = cipher.encrypt(plain_text)
    >>> result_data = cipher.decrypt(crypted_data)
    >>> assert plain_text == result_data


#### Using filenames

    Python 2.7.10 (default, May 23 2015, 09:40:32) [MSC v.1500 32 bit (Intel)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import chi_io  # https://github.com/clach04/chi_io Python access to Tombo encrypted files
    >>> chi_io.implementation
    'using PyCrypto'
    >>> plain_text = b'12345678'
    >>> enc_fname = 'chi_io_test1.chi'
    >>> mypassword = b'testing'
    >>> mypassword = chi_io.CHI_cipher(mypassword)  # OPTIONAL! encryption and decryption will be faster on subsequent calls if the same password is used
    >>> chi_io.write_encrypted_file(enc_fname, mypassword, plain_text)
    >>> read_plain_text = chi_io.read_encrypted_file(enc_fname, mypassword)
    >>> assert plain_text == read_plain_text

    python chi_io.py some_existing_file.chi  # will be prompted for password to decrypt existing file
    env LANG=C.UTF-8 python chi_io.py some_existing_file.chi  # will be prompted for password to decrypt existing file

NOTE write_encrypted_file() and read_encrypted_file() can take either file names or file-like objects.

## Tests

    python test_chi.py
    env NO_PYCRYPTO=true python test_chi.py  # force usage of Pure Python Blowfish (slower)


## NOTES

  * PyCrypto will work fine but PyCryptodome is preferred.
    * The known vulnerability in PyCryptodome is not in the Blowfish implementation
  * Blowfish is not recommended by its author! Neither is ECB mode which Tombo uses (note Tombo does some additional bit fiddling but using Tombo CHI encryption for sensitive files is not recommended)
  * GNU General Public License v3.0 https://github.com/jashandeep-sohi/python-blowfish the pure Python 3.4+ blowfish implementation works great, but is slower than PyCryptodome


## Also see

Compatible with:

  * http://tombo.osdn.jp/En/
      * https://osdn.net/projects/tombo/scm/
      * https://osdn.net/cvs/view/tombo/
      * Forks and mirrors
          * https://github.com/clach04/tombo_cvs - old code, 2002-2006
          * https://github.com/clach04/tombo - latest, with some minor new features ahead of upstream - missing CVS history, 2009+
  * https://osdn.net/projects/kumagusu/ - by tarshi
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.kumagusu
      * https://github.com/clach04/kumagusu_mirror
  * https://web.archive.org/web/20171221160557/http://hatapy.web.fc2.com/mininoteviewer.html (was http://hatapy.web.fc2.com/mininoteviewer.html) - by hatalab
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.hatalab.mnv
      * https://github.com/clach04/mininoteviewer_mirror
  * Tombo Edit - by Michael Efimov
      * https://sourceforge.net/projects/tomboedit/
      * https://github.com/clach04/tombo_edit_mirrorfork
   * TomboCrypt - by Michael Efimov
       * https://osdn.net/projects/tombo/releases/p1532 simple command line utility - 32-bit binaries for Microsoft Windows and Linux
       * https://osdn.net/projects/tombo/scm/git/Tombo/tree/master/contrib/TomboCrypt/ - source code in git can be built with `gcc -static -DTOMBO -oTomboCrypt *.cpp *.c  -lstdc++`
       * https://osdn.net/cvs/view/tombo/Tombo/contrib/TomboCrypt/ - source code in CVS
       * NOTE this Python chi_io library is the closest to this, as it is Python it is portable and works anywhere there is Python (know to work on intel Windows and Linux, along with arm both 32-bit and 64-bit Linux)


## TODO

  * Refactor chi_io code
  * Implement Tombo chi Cipher that follows PEP 272
  * Update Pure python Blowfish (wrapper or upstream) to support Cipher PEP 272
    API for Block Encryption Algorithms v1.0 https://www.python.org/dev/peps/pep-0272/
  * Check for pycryptodomex first
