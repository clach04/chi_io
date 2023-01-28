#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
"""Test suite for pytombo

Sample usage:

    ./test_chi.py -v
    ./test_chi.py -v TestCompatChiIO

"""

import os
import sys
import string
import codecs

try:
    if sys.version_info < (2, 3):
        raise ImportError
    import unittest2

    unittest = unittest2
except ImportError:
    import unittest

    unittest2 = None


try:
    raise ImportError  # do not use cStringIO for readwrite_seek test
    # AttributeError: 'cStringIO.StringI' object has no attribute 'write'
    from cStringIO import StringIO as FakeFile

    using_cstring = True
except ImportError:
    try:
        from StringIO import StringIO as FakeFile

        using_cstring = True
    except ImportError:
        from io import BytesIO as FakeFile  # py3

        using_cstring = False

import chi_io

"""
Missing tests for:

  * chi_io.dumb_unix2dos()

Present are tests that make calls to:
  * chi_io.write_encrypted_file()
  * chi_io.read_encrypted_file()
  * chi_io.ChiAsFile class

NOTE this does not mean exhaustive tests ;-)

No explicit tests for:

  * read_encrypted_file() - called by ChiAsFile.read()
  * write_encrypted_file() - called by ChiAsFile.write() and close()
  * CHI_cipher() - called by read_encrypted_file() and write_encrypted_file()

"""

class TestChiIOUtil(unittest.TestCase):
    def skip(self, reason):
        """Skip current test because of `reason`.

        NOTE currently expects unittest2, and defaults to "pass" if not available.

        unittest2 does NOT work under Python 2.2.
        Could potentially use nose or py.test which has (previously) supported Python 2.2
          * nose http://python-nose.googlecode.com/svn/wiki/NoseWithPython2_2.wiki
          * py.test http://codespeak.net/pipermail/py-dev/2005-February/000203.html
        """
        # self.assertEqual(1, 0)
        if hasattr(unittest, 'SkipTest'):
            raise unittest.SkipTest(reason)
        else:
            print(reason)
            self.fail('SKIP THIS TEST: ' + reason)
            # self.assertTrue(False, reason)
            # raise Exception(reason)


class TestChiIO(TestChiIOUtil):
    def test_get_what_you_put_in(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data = fileptr1.getvalue()
        # print repr(crypted_data)

        fileptr2 = FakeFile(crypted_data)
        result_data = chi_io.read_encrypted_file(fileptr2, test_password)
        # print repr(result_data)
        self.assertEqual(test_data, result_data)

    def test_same_input_different_crypted_text(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data1 = fileptr1.getvalue()

        fileptr2 = FakeFile()
        chi_io.write_encrypted_file(fileptr2, test_password, test_data)
        crypted_data2 = fileptr2.getvalue()
        self.assertNotEqual(crypted_data1, crypted_data2)

        fileptr3 = FakeFile(crypted_data1)
        result_data = chi_io.read_encrypted_file(fileptr3, test_password)
        self.assertEqual(test_data, result_data)

        fileptr3 = FakeFile(crypted_data2)
        result_data = chi_io.read_encrypted_file(fileptr3, test_password)
        self.assertEqual(test_data, result_data)

    def test_fileread(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data = fileptr1.getvalue()
        # print repr(crypted_data)

        fileptr2 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr2, test_password)
        result_data = chi_fileptr.read()
        # print repr(result_data)
        self.assertEqual(test_data, result_data)

    def test_filewrite(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password, 'w')
        chi_fileptr.write(test_data)
        chi_fileptr.close()
        crypted_data = fileptr1.getvalue()
        # print 'crypted_data ', repr(crypted_data)

        fileptr2 = FakeFile(crypted_data)
        result_data = chi_io.read_encrypted_file(fileptr2, test_password)
        # print repr(result_data)
        self.assertEqual(test_data, result_data)

    def test_file_bad_read(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password, 'w')
        chi_fileptr.write(
            test_data
        )  # file is now a write only file, any reads after this point are an error
        self.assertRaises(IOError, chi_fileptr.read)

    def test_file_bad_write(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data = fileptr1.getvalue()

        fileptr1 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password)
        result_data = chi_fileptr.read()
        self.assertEqual(test_data, result_data)
        self.assertRaises(IOError, chi_fileptr.write, test_data)

    def test_filewrite_unicode(self):
        test_data = u'Bj\N{LATIN SMALL LETTER O WITH DIAERESIS}rk is a great singer!'
        test_password = b'mypassword'
        output_encoding = 'utf8'
        encoder, decoder, streamreader, streamwriter = codecs.lookup(output_encoding)

        fileptr1 = FakeFile()
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password, 'w')
        chi_fileptr = streamwriter(chi_fileptr)
        chi_fileptr.write(test_data)
        chi_fileptr.close()
        crypted_data = fileptr1.getvalue()
        # print 'crypted_data ', repr(crypted_data)

        fileptr2 = FakeFile(crypted_data)
        result_data = chi_io.read_encrypted_file(fileptr2, test_password)
        # print repr(result_data)
        result_data = result_data.decode(output_encoding)
        self.assertEqual(test_data, result_data)

    def test_fileread_unicode(self):
        test_data = u'Bj\N{LATIN SMALL LETTER O WITH DIAERESIS}rk is a great singer!'
        test_password = b'mypassword'
        output_encoding = 'utf8'
        encoder, decoder, streamreader, streamwriter = codecs.lookup(output_encoding)

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(
            fileptr1, test_password, test_data.encode(output_encoding)
        )
        crypted_data = fileptr1.getvalue()
        # print repr(crypted_data)

        fileptr2 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr2, test_password)
        chi_fileptr = streamreader(chi_fileptr)
        result_data = chi_fileptr.read()
        # print repr(result_data)
        self.assertEqual(test_data, result_data)

    def test_file_bad_write_after_close(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password, 'w')
        chi_fileptr.write(test_data)
        #
        chi_fileptr.close()
        self.assertRaises(ValueError, chi_fileptr.write, test_data)

    def test_file_bad_read_after_close(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data = fileptr1.getvalue()

        fileptr1 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr1, test_password)
        result_data = chi_fileptr.read()
        chi_fileptr.close()
        self.assertEqual(test_data, result_data)
        self.assertRaises(ValueError, chi_fileptr.read)

    def test_readwrite_seek_middle(self):  # FIXME / TODO seek in name but no seek operation in test
        if using_cstring:
            self.skip('cString does not support read and write on the same object')
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        fileptr1 = FakeFile()
        chi_io.write_encrypted_file(fileptr1, test_password, test_data)
        crypted_data = fileptr1.getvalue()
        # print repr(crypted_data)

        fileptr1 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(
            fileptr1, test_password, '+'
        )  # NOTE + is Read and Write which Cpython 2.x cStringIO does not support, expect AttributeError: 'cStringIO.StringI' object has no attribute 'write'
        chi_fileptr.write(b'text')
        chi_fileptr.close()
        crypted_result = fileptr1.getvalue()

        fileptr2 = FakeFile(crypted_result)
        chi_fileptr = chi_io.ChiAsFile(fileptr2, test_password)
        result_data = chi_fileptr.read()
        # print repr(result_data)
        self.assertEqual(b"text is just a small piece of text.", result_data)


class TestCompatChiData(TestChiIOUtil):
    ## Test that can read files generated from Windows Tombo
    ## http://tombo.sourceforge.jp/En/

    password = b'password'

    ## encrypted data taken from Win32 Tombo
    ## password for below data is: 'password'
    binary_data = b'BF01\xe6\x05\x00\x00\xb2\xdfB\xf2\x9d-]\x89c\x92|.\xae\x88\xaa\x96Oi\
\xd6\x1dOA\xb41_b\x9b\x84\xdeSS\x1c\xc1\xd6\x98\xcf\xd9e\x84\xff\xecm\
\n\x8a|\xb4\xc3\xf0\xda\xd2@\xecqDaE_\xc1x\xff!sP+]\xa8F\xe2\n\xd5\xd1ZL\
\x84Wh\x85\x9db\xc2\xf4\x14\x00\xccs+\xac\x0e\xe0a\xfb)\r\x04\x81\x7f\
\xcd#e\xfe_\xca\x90\x95`\xd7\xb2 ,~/q\xc1\xc5\x03\x84*G4\xa6Zf<-\xcc\
\x06MW>\xe7\xa6\xba\xe8\xdfQZdG)qwx\xf3\xd4%\xe7\x93\xccKL_L1\x13\xb6\
\xfa\xb2b\xd2\xcck\x14:9\xa4$\xb6\x06\x92\xccs.\x18V\xecH\x1e\xe7\x12\
\xbe\xe4{\xc1^v\xad\xd9\x99\xa89\xba\xc7\xa1\xfaFl\x82\xb1\x92kB\xf7\
\x86 \x13\xec\x89\xfd\xbfg/{\x82:\xb3\x1f\xf4s\x15}\xeb\x98\xa6\xf1\t\
\x07\xedm\xb8\x03\xff\xd6\x14_\x07\x98:\x88\xf6H\x16\xb5\x00 V\xc5<LV\
\xc89\xd4\xd3\xd8\xee\xec\\\x1c\xf7\xc4\x19\xb4\x1d\xdet\xcf\t\xcb{\n\n\
\xa9T\xd4\xb3R\xbev\xe9A\x98\xe1>yW\x91}s{$\x1c\xcf-h9\xbe\x05bX|\x18\
\xde\xb0\x17\x06)I&p\x9c\x14FU\x9b\xfc\xd5\xb7\x0b\x17\x06_\xcd%\xcd\
\xea\x81D\xa0\x14U\x8e\xe6\x9em\x0bE\xa4\xdf\xb7d\x13\xef\xc6\xdem\rD@:\
\xebM\x12\xd6\x03\xfb5\xac\x8fhT\xbb\xb1\xb1y\xd3^$\xdal\xa9)y\x1c\x10\
\xc6\xd5P\x9e\x88|\xdc\xffpB\x8d\xa5\x9cy\x87\x13\xe4\xdc\xa5\x938r\xf0\
\xc2+iS\xad\xf3W\x0f\xa65\'\x937\xd5\x911\xce\n\xc8\xe7\xd1\x9a\xb7\
\xc4l3\xcfc\xf9\xec \xd0x\xbc\x8a&\r\x98\xe8\xaf\xce\x1f\xe3\r\xa7\
\x08\xc8\x1a}\xd2\xff\xea\x8dn\xf2\xa8/\xf2\xe4\xab\x8c\xd5&~\xe5C!\
\x17\xca\t\x9a\xf3+/\xed\xae\xe2M\xf0\xba6/\xeda\xf8\x04xh3E&\x8d\xd5\
\xf6d\xb3~\xd5Cdi\xbaUk\xb7\xa1M\xe0R\xf7"\x88\xa1\xc2\xe5\x15L\xdc\
\xa6^\x93\x9d\x03\xd7\xd5\xe3\xb0\x1b(\x92|B\xa0\x00\xd0?\xbbf\x91\
\x80\xd4\xff\xaa\xd8k.\x82A\xd4\xaeW;\x7f(,\xce\x8c\xe4YXQc\x0fi\x06\
\x17\x8ei\xdd\xc0\xe2m\xa7\xbf\xeb\ti8\x12\x880<\x02\xa1b\x85Y\xb1v\
\x90\xfbn\xbd\xbaFi-\xd5\x83U\xa3\xf36@\x1cQ\xde\xb9\xbai\x98-\x06\
\x1b\xa4\xf3\xe0`SZ\x81\xf0\xd9\xaf\xc8\xb5j\x01\xf0\xb6\xe5\x9c\
\x9e\xd4\x13\x9d\x04\x9c\xe2\rLe\xbe\xd1\x08\xe7\xaa\xf23\x86w\
\xb1yd\xb0\xfd\x82U\x96\x97\x8e\x82?\xe8\xe4z\x7f~\xb8\xfci\x05(K\
\xe0\xa8\x03&\xd5ujTZR\xb0\x04\xbe5NzM\x7f\xcb\x89\x9c\xa4li\x81P\
\xd3\xe3/\xcb\x02\xf6\xed\x96\xccJ\x8c\xeam\r<\x8fT\xcd\x88\xe6\x895\
\xe9\x97\xa6B\xd6\x0bsK\xd5\x89\x94\x15ww\xc9\x91\x80\x1f\x91\xf9oN\
\x0c\xe7\x9b\x19 \x1d\xeb\x9d9\xbe\xa0\xecU\x00\xf3P4\x1d\xca\xcb\xe6\
\xfdO\x92\xc0QF\xf1\xd8k\x96\xaek\x03|\x87\xc6\xd4\xb3\xfa\xb5\x95\xbd\
\xa5\x0e\xc8@\x15Ng\xa5\x99\xab5u\xccx\xf5=\x8b.\xef"\x1a0\xe5\xdc\x18q\
\\\xfd\xba\xdb\xba\xb9u\x89\x18\xc9\x01%\x8b\x90\xf0.gM\xfc\xbe\x86~L\
\xea\xe6\x05\x9f\xf3s\xa9\xa0)\x1d\xd2\x02R\x07\x1d\t\x07\x1e\xa6\xb0\
\xb15\xb9\xcb\xc4\xff\xa3\xa1\xba\x9c\xec\x82r\x19fm\x1c\x8a1\x9d\xe2\
\x7f=f\xa29\xba\x86\x11\xe1\xde\x80\x96\x83\x17\xfe\xdc\\A\x0b\xc9\x1e4\
\x01}\x1dV\xfc\xaen\xff\xb3\x8a\x15\xa9\xff\xd1\x8evB\xf3\xc98\xd6\x97\
\x17c\x84\xa1\xca\x9a\\J\x0b@_\xe3U\x8e\x94\xe9b"\xa3\x9d2\x1d\x93\xcf\
\xb0%\xe0$\xac=\xca\x1e\xe7\xc2\xb6E]\x19\xe5*/omuT\xe4\xc4@\x97\x81\
\xee\xde\xfb9(G3\x874\xbaRL\t\xd0\xdd\x01\x86\xa9%5\xb0 [\x9d_\
\x992z.R\n\xe4\xfd\x91\x95\x0et\xd0\x10\xbf\xda\x86ngLB\xc1w\x80\
\xf3fw,\xb8\xdd\xf9,\x85&\xd5\xb4\xaex\xa9c\x0f\xad:3\xb7Q4l\xef\
\xbc\xad(m4\xdaI\xd5\xd4\xfa\x9f\x86K\xe9|SS\xce\xb9\x02\xec\xb3\
\xe1G^D\x99\xbc@\x9cI\xd4\x0f\x94[\xc9zPL\xd6\x8b\xd1;\x13#K2\xc3\
\x07\x07\xfd\x99\x9c\xbcZ\xa3(\x8b\xa8\x92\xd7\xd6\x86LG\xa1\x92C\
\xe1\xf6\x85\\H\\6\xcc]\x80D\x0b01\x04%\xd32\xba\xa2\xfa[\x91f(\xc3\
\x08\xf2B\xbe\xe8\x05C\x8c\xca\x0f\x92\xa7K\xbb\x15\xf9\xc8\xae\x86\
\x8flp\xc2\xc9\x0e]\xa62\xb8\x92\xb48\xc5\x08A\x8f\xab1\xb5.=P\xd6\
\x93\x1c\xb8H\xa3\x0b\xa8~\x8dg\xca~\xa4\xd4\xf7bN\xaet\xa6\xee\xeb\
\x9b\x1b\x14#:dS\xc4\xfc\xae\xbc\xb0\xd5:d\xb4\xa1\x9c\x06\\\x87\rp\
\xdb\xab\x8d\xd6\x95\x89\xfa>U\x02\xf9\x15\xb4\xa5\x84\xdf(\x14Q%]`C\
\xff\xed\xaf{\xce\x86\xc1`#\xc3\x13g\xb4\xb5\xa3ehtr\xbf\xa5\\\xae\
\xe0\xfcH\xeb3\xae5\x1co+v\xeabx\xf35o\xd1`%\x19\xdf\xd7\xab\xd6hI\
\x7f\xb4\xa3\x1dv\x15\x8e\xf3\xce\xa0\xbd\xf6\xea\xd5\xee\x7f\xf8\
\xcc\x87\xf5\xde\xfb\x04&\xc8\x87)\xfa!\xbd\xcc\x1bh\xe2\tJ\xe1\
\xa1\xdb+\x1f!@\xb3i\x841s\xe5j_\xd3\xe2\x01!trJ\xc5\xa4\xa5>\
\x009<\xb2,7\xed\xcf\xfa\x8b1\xcc\x9d40\x0btOpk\xf9^\xf2\xb2T/\
\xd3?e\x9b:\x89C\xebm\x8f.\xaa8m\x9c\xb6|\xa9\xd3E\xf4934Uo\'\xf1\
\x16\xe4\n2\x15d\x17\x0ed\xc1>y\xf869\xc4bM\x9e\x17l\xf9\xb8C\xd2\
\xe0\x17\xb4E\x0e\xae.G\xde\xe2\x9e\xfc~\x1b\x8687\xd2!\xe7w\x95!t\
\xcfXN\xcf\xae\x81\xd7\xc1\xe9\x84(F\xc3i\x12\x12\x178\x06J\xd0G\xa2:\
\xb6\xf5\x94b+\x1c6\x97yvs\xb2\x1a\x93)\xf6V\xaf(\x02Y\xef\x05\x8f)\
\xa5\x1b\xd2y\x10vn\x9d\xf4\x0e\x1d\xff?\x94i\xcb\xc3\x1f!\xd5:\x96\xdb~\xad'

    plain_text_data = b'''aesop\r\n\r\nThe Frogs Desiring a King\r\n\r\nThe Frogs were l\
iving as happy as could be in a marshy swamp that just suited the\
m; they went splashing about caring for nobody and nobody troubli\
ng with them. But some of them thought that this was not right, t\
hat they should have a king and a proper constitution, so they de\
termined to send up a petition to Jove to give them what they wan\
ted. "Mighty Jove," they cried, "send unto us a king that will ru\
le over us and keep us in order." Jove laughed at their croaking,\
 and threw down into the swamp a huge Log, which came down splash\
ing into the swamp. The Frogs were frightened out of their lives \
by the commotion made in their midst, and all rushed to the bank \
to look at the horrible monster; but after a time, seeing that it\
 did not move, one or two of the boldest of them ventured out tow\
ards the Log, and even dared to touch it; still it did not move. \
Then the greatest hero of the Frogs jumped upon the Log and comme\
nced dancing up and down upon it, thereupon all the Frogs came an\
d did the same; and for some time the Frogs went about their busi\
ness every day without taking the slightest notice of their new K\
ing Log lying in their midst. But this did not suit them, so they\
 sent another petition to Jove, and said to him, "We want a real \
king; one that will really rule over us." Now this made Jove angr\
y, so he sent among them a big Stork that soon set to work gobbli\
ng them all up. Then the Frogs repented when too late.\r\n\r\nBet\
ter no rule than cruel rule.\r\n'''


class TestCompatChiIO(TestCompatChiData):
    ## Test file IO

    def do_fileread(self, crypted_data, test_password, expected_plain_text_data):
        fileptr2 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr2, test_password)
        result_data = chi_fileptr.read()
        self.assertEqual(expected_plain_text_data, result_data)

    def test_win32_compat_fileread(self):
        test_password = self.password

        self.do_fileread(self.binary_data, test_password, self.plain_text_data)

    def test_seek_fileread(self):
        test_password = self.password

        crypted_data = self.binary_data
        expected_plain_text_data = self.plain_text_data[30:]

        fileptr2 = FakeFile(crypted_data)
        chi_fileptr = chi_io.ChiAsFile(fileptr2, test_password)
        chi_fileptr.seek(30)
        result_data = chi_fileptr.read()
        self.assertEqual(expected_plain_text_data, result_data)

    def test_badpassword(self):
        test_password = b'badpassword'

        self.assertRaises(
            chi_io.BadPassword,
            self.do_fileread,
            self.binary_data,
            test_password,
            self.plain_text_data,
        )
        self.assertRaises(
            chi_io.ChiIO,
            self.do_fileread,
            self.binary_data,
            test_password,
            self.plain_text_data,
        )

class TestCompatChiDecrypt(TestCompatChiData):
    ## Test file IO

    # TODO clone approach in TestCompatChiIO

    def test_in_memory_decrypt(self):
        test_password = self.password

        cipher = chi_io.PEP272LikeCipher(test_password)

        result_data = cipher.decrypt(self.binary_data)
        self.assertEqual(self.plain_text_data, result_data)

    def test_in_memory_decrypt_badpassword(self):
        test_password = b'badpassword'

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.BadPassword,
            cipher.decrypt,
            self.binary_data
        )
        self.assertRaises(
            chi_io.ChiIO,  # base exception for CHI
            cipher.decrypt,
            self.binary_data
        )

    def test_in_memory_decrypt_badinput_empty(self):
        test_password = b'badpassword'
        test_data = b''

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.UnsupportedFile,
            cipher.decrypt,
            test_data
        )
        self.assertRaises(
            chi_io.ChiIO,  # base exception for CHI
            cipher.decrypt,
            test_data
        )

    def test_in_memory_decrypt_badinput_junk(self):
        test_password = b'badpassword'
        test_data = b'JUNKDATEHEREAS'

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.UnsupportedFile,
            cipher.decrypt,
            test_data
        )
        self.assertRaises(
            chi_io.ChiIO,  # base exception for CHI
            cipher.decrypt,
            test_data
        )

    def test_in_memory_decrypt_badinput_valid_bf01(self):
        test_password = b'badpassword'
        test_data = b'BF01JUNKDATEHEREAS'

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.UnsupportedFile,
            cipher.decrypt,
            test_data
        )
        self.assertRaises(
            chi_io.ChiIO,  # base exception for CHI
            cipher.decrypt,
            test_data
        )

    def test_in_memory_decrypt_badinput_validstart_extra(self):
        test_password = b'badpassword'
        test_data = self.binary_data + b'BF01JUNKDATEHEREAS'

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.UnsupportedFile,
            cipher.decrypt,
            test_data
        )
        self.assertRaises(
            chi_io.ChiIO,  # base exception for CHI
            cipher.decrypt,
            test_data
        )


class TestCompatChiEncryptDecrypt(TestCompatChiData):
    ## in memory equiv of TestChiIO.test_get_what_you_put_in()
    def test_get_what_you_put_in(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        cipher = chi_io.PEP272LikeCipher(test_password)

        crypted_data = cipher.encrypt(test_data)
        result_data = cipher.decrypt(crypted_data)
        self.assertEqual(test_data, result_data)

    def test_get_what_you_put_in_larger(self):
        test_data = self.plain_text_data
        test_password = self.password

        cipher = chi_io.PEP272LikeCipher(test_password)

        crypted_data = cipher.encrypt(test_data)
        result_data = cipher.decrypt(crypted_data)
        self.assertEqual(test_data, result_data)

    def test_same_input_different_crypted_text(self):
        test_data = b"this is just a small piece of text."
        test_password = b'mypassword'

        cipher = chi_io.PEP272LikeCipher(test_password)

        crypted_data1 = cipher.encrypt(test_data)
        crypted_data2 = cipher.encrypt(test_data)
        self.assertNotEqual(crypted_data1, crypted_data2)

        result_data = cipher.decrypt(crypted_data1)
        self.assertEqual(test_data, result_data)
        result_data = cipher.decrypt(crypted_data2)
        self.assertEqual(test_data, result_data)

    def test_unicode_strings_rejected(self):
        test_data = u"this is just a small piece of text."
        test_password = b'mypassword'

        cipher = chi_io.PEP272LikeCipher(test_password)

        self.assertRaises(
            chi_io.ChiIO,
            cipher.encrypt,
            test_data
        )



if __name__ == '__main__':
    print(sys.version)
    print(chi_io.implementation)
    unittest.main()
