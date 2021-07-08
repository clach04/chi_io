# chi_io

Pure Python read/write encryption/decryption of encrypted Tombo chi files. If you are looking for an easy to use with safe and sane defaults for encryption do NOT use this, this is intended to be compatible with Tombo, Kumagusu, MiniNoteViewer, etc.

Compatible with:

  * http://tombo.osdn.jp/En/
  * https://osdn.net/projects/kumagusu/
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.kumagusu
  * http://hatapy.web.fc2.com/mininoteviewer.html
      * https://play.google.com/store/apps/details?id=jp.gr.java_conf.hatalab.mnv&hl=en_US&gl=US


Extracted from https://hg.sr.ht/~clach04/pytombo

Library originally supported Python 2.1, 2.2, 2.4, 2.4, 2.5, 2.6, 2.7. Now only targets Python 2.7 and 3.x. Use older version shipped with PyTombo for Python < 2.7.


To get started:

    python -m pip install -r requirements.txt  # runs faster Py2 and Py3, slower alternative is `python -m pip install blowfish` Python 3 only

    python test_chi.py

## NOTES

  * PyCrypto will work fine but PyCryptodome is preferred.
    * The known vulnerability in PyCryptodome is not in the Blowfish implementation
  * Blowfish is not recommended by its author! Neither is ECB mode which Tombo uses (note Tombo does some additional bit fiddling but using Tombo CHI encryption for sensitive files is not recommended)

## TODO

  * Look at using pycryptodomex
  * Pure Python 2 Blowfish (note will be much slower)
  * Refactor chi_io code
  * Update Pure python Blowfish (wrapper or upstream) to support Cipher PEP 272
    API for Block Encryption Algorithms v1.0 https://www.python.org/dev/peps/pep-0272/
