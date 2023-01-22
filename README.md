# chi_io

Pure Python read/write encryption/decryption of encrypted Tombo chi files. If you are looking for an easy to use with safe and sane defaults for encryption do NOT use this, this is intended to be compatible with Tombo, Kumagusu, MiniNoteViewer, etc.

Compatible with:

  * http://tombo.osdn.jp/En/
  * https://osdn.net/projects/kumagusu/ - by tarshi
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.kumagusu
      * https://github.com/clach04/kumagusu_mirror
  * https://web.archive.org/web/20171221160557/http://hatapy.web.fc2.com/mininoteviewer.html (was http://hatapy.web.fc2.com/mininoteviewer.html) - by hatalab
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.hatalab.mnv
      * https://github.com/clach04/mininoteviewer_mirror
  * Tombo Edit - by Michael Efimov
      * https://sourceforge.net/projects/tomboedit/
      * https://github.com/clach04/tombo_edit_mirrorfork
   * TomboCrypt is a simple command line utility, written by Michael Efimov
       * https://osdn.net/projects/tombo/releases/p1532
      

Extracted from https://hg.sr.ht/~clach04/pytombo

Library originally supported Python 2.1, 2.2, 2.4, 2.4, 2.5, 2.6, 2.7. Now only targets Python 2.7 and 3.x. Use older version shipped with PyTombo for Python < 2.7.


To get started:

    python -m pip install -r requirements.txt  # runs faster Py2 and Py3, slower alternative is `python -m pip install blowfish` Python 3 only

    python test_chi.py

## Examples

    Python 2.7.10 (default, May 23 2015, 09:40:32) [MSC v.1500 32 bit (Intel)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import chi_io  # https://github.com/clach04/chi_io Python access to Tombo encrypted files
    >>> chi_io.implementation
    'using PyCrypto'
    >>> plain_text = b'12345678'
    >>> enc_fname = 'chi_io_test1.chi'
    >>> mypassword = b'testing'
    >>> chi_io.write_encrypted_file(enc_fname, mypassword, plain_text)
    >>> read_plain_text = chi_io.read_encrypted_file(enc_fname, mypassword)
    >>> assert plain_text == read_plain_text

    python chi_io.py some_existing_file.chi  # will be prompted for password to decrypt existing file
    env LANG=C.UTF-8 python chi_io.py some_existing_file.chi  # will be prompted for password to decrypt existing file


## Tests

    python test_chi.py
    env NO_PYCRYPTO=true python test_chi.py  # force usage of Pure Python Blowfish (slower)


## NOTES

  * PyCrypto will work fine but PyCryptodome is preferred.
    * The known vulnerability in PyCryptodome is not in the Blowfish implementation
  * Blowfish is not recommended by its author! Neither is ECB mode which Tombo uses (note Tombo does some additional bit fiddling but using Tombo CHI encryption for sensitive files is not recommended)
  * GNU General Public License v3.0 https://github.com/jashandeep-sohi/python-blowfish the pure Python 3.4+ blowfish implementation works great, but is slower than PyCryptodome

## TODO

  * Refactor chi_io code
  * Implement Tombo chi Cipher that follows PEP 272
  * Check for pycryptodomex first
  * Pure Python 2 Blowfish (note will be much slower)
  * Update Pure python Blowfish (wrapper or upstream) to support Cipher PEP 272
    API for Block Encryption Algorithms v1.0 https://www.python.org/dev/peps/pep-0272/
