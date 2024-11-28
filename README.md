-- coding: utf-8 --

# chi_io

Pure Python read/write encryption/decryption of [Tombo](https://github.com/clach04/tombo/) chi/chs [blowfish](https://www.schneier.com/academic/archives/1994/09/description_of_a_new.html) encrypted files. If you are looking for an easy to use with safe and sane defaults for encryption do NOT use this (there a more modern and better best-practices available since 2004), this is intended to be **compatible** with [Tombo](http://tombo.osdn.jp/En/), Android [Kumagusu](https://github.com/clach04/kumagusu_mirror), [MiniNoteViewer](https://github.com/clach04/mininoteviewer_mirror), [etc.](https://github.com/clach04/puren_tonbo/wiki/Tombo) Tombo chi/chs files are encrypted with blowfish and thus vulnerable to a [32-bit Birthday Attack](https://sweet32.info/). Tombo uses blowfish-CBC with a fixed IV and always uses the same key derived from a passphrase.

https://github.com/clach04/chi_io

Extracted from https://hg.sr.ht/~clach04/pytombo

Library originally supported Python 2.1, 2.2, 2.4, 2.4, 2.5, 2.6, 2.7. Now only targets Python 2.7 and 3.x. Use older version shipped with PyTombo for Python < 2.7.

Can be used standalone, used by Puren Tonbo https://github.com/clach04/puren_tonbo/ which supports different encryption formats/ciphers.


  * [Getting Started](#getting-started)
  * [Examples](#examples)
    + [Command line tool chi_io](#command-line-tool-chi-io)
    + [Python code](#python-code)
      - [In memory](#in-memory)
      - [Using filenames](#using-filenames)
  * [Tests](#tests)
  * [NOTES](#notes)
  * [Also see](#also-see)
  * [File format specification](#file-format-specification)
  * [TODO](#todo)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


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
    chi_tool.py scratch/mynote.chi | vim -  # decrypt a note and pipe into vim


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
  * Blowfish is not recommended by its author! Neither is ECB mode which Tombo uses (note Tombo does some additional bit fiddling but using Tombo CHI/CHS encryption for sensitive files is not recommended)
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


## File format specification

`*.chi` and `*.chs` use the same format, the only difference between the
two is that Tombo chs files are automatically/randomly named, using
only (16) digits. For example, "0000000000000000.chs".

An md5 checksum hash is generated from the password, this is then used as the key. I.e. KDF is md5, without any salt/IV.

The data to encrypt is prefixed with some random salt.

The key is then used to encrypt using [Blowfish cipher] (https://en.m.wikipedia.org/wiki/Blowfish_(cipher)) in cipher block chaining (CBC) mode, with  **fixed** IV of "BLOWFISH".

Copy and paste from [Src/CryptManager.cpp](https://github.com/clach04/tombo/blob/my_changes/Src/CryptManager.cpp):

    //////////////////////////////////////////////////
    // Encrypt data and add header
    //////////////////////////////////////////////////
    // CryptManagerによる暗号化ファイルのフォーマット
    // The format of the container is:
    // 0-3  : BF01(4 bytes)
    // 4-7  : data length (include randum area + md5sum)(4 bytes)
    // 8-15 :* random data(8 bytes)
    //16-31 :* md5sum of plain text(16 bytes)
    //32-   :* data

    // '*' is encrypted.

  * 4-bytes : `version` : fixed to "BF01". No other value is valid.
  * 4-bytes little-endian : `plaintext_length` : length of the actual plaintext (C++ comment is incorrect/misleading)
  * encrypted payload : `encrypted_bytes` : blowfish encrypted payload, needs to be decrypted and once decypted contains:
      * 8-bytes little-endian : `random_salt` : Random bytes that is prefixed to data before encryption
      * 16-bytes little-endian : `plaintext_md5` : md5sum of the plaintext, essentially Authenticate Then Encrypt
      * `plaintext_length`-bytes : `plaintext` : plain text. NOTE possible padding on the end AFTER `plaintext_length`

See code for both the KDF and the cipher [implementation](https://github.com/clach04/tombo/blob/080a85d9bce3f60a91b7e8ecd5b9f30b5c4e00f9/Src/GNUPG/blowfish.c#L616) (and padding), Blowfish (64-bit blocks) are used with additional block shuffling.

## TODO

  * Refactor chi_io code
  * Implement Tombo chi/chs Cipher that follows PEP 272
  * Update Pure python Blowfish (wrapper or upstream) to support Cipher PEP 272
    API for Block Encryption Algorithms v1.0 https://www.python.org/dev/peps/pep-0272/
  * Check for pycryptodomex first
