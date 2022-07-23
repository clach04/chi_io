#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# pytombo - Python library for processing plain text + encrypted notes.
# Copyright (C) 2007  Chris Clark

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
chi I/O module

Reads Writes encrypted Tombo *.chi

NOTE: if you want to read notes in Tombo that where generated with
this module, ensure to send in strings to write_encrypted_file()
with Windows style newlines (i.e. '\x0D\x0A')

Tombo is available from http://tombo.sourceforge.jp/En/
"""

"""
TODO list

*   Support file-like objects interface, not just "here is the string"/"return the string"
*   clean up asserts - hey can be "compiled" out in non-debug mode
*   Clean up exception (classes, handle repr) and raising (match pep-8)
*   Run through PyChecker, PyLint, etc. checkers
*   Try and use a consistent coding style:
    http://www.python.org/dev/peps/pep-0008/
    http://www.python.org/dev/peps/pep-0257/
    This is slightly tricky as pep 8 encourages "lowercase, with words separated by underscores" over mixedCase
    May need to rename module too as underscores are frowned upon, e.g. chi_io to chiio which doesn't read well.
*   See http://wiki.python.org/moin/PythonSpeed
*   See http://wiki.python.org/moin/PythonSpeed/PerformanceTips -- contain speed and profiling information/tips
*   UnitTest to generate some data and then crypt/decrpt it. Ideally make use of TomboCrypt for confirmed sanity checks.
*   Profile/time so that if any performance tweaks are made they can be checked! Test with Psyco http://psyco.sourceforge.net/. More struct usage, etc.
    *   most time spent in __round_func() - probably not much can be done
        there, however init of Blowfish is nearly 50% of a small decryption.
        If the same password is used for reading many files this is a large
        overhead that could be reduced to 1 call!
*   Some list, ord(), chr(), to string operations could be simplified to perform more operations whilst as lists before conversion back to strings
    *   use array module (array.array) instead of lists for performance
    *   Remove string operations, try and use cStringIO library instead to save on garbage collection and creating new items
"""

import os
import sys

is_py3 = sys.version_info >= (3,)
import struct
import array

try:
    import hashlib

    md5checksum = hashlib.md5
except ImportError:
    # pre 2.6/2.5
    import md5

    md5checksum = md5.new
import string
import random

try:
    # raise ImportError
    from cStringIO import (
        StringIO as FakeFile,
    )  # NOTE only use when not using .write() method - does not support Unicode
except ImportError:
    try:
        from StringIO import StringIO as FakeFile
    except ImportError:
        from io import BytesIO as FakeFile  # py3


"""
Import pure python blowfish implementation
this is from http://cheeseshop.python.org/pypi/pypwsafe/0.0.2
this differs from the original Michael Gilfix <mgilfix@eecs.tufts.edu>
version in that it has been up-dated to deal with Long Integers so you do
not get future warnings with Python 2.3 (and based on my experience with
freddb cdkeys) and errors/data-corruption in Python 2.4).

See:
    http://jason.diamond.name/weblog/2005/04/07/cracking-my-password-safe
    http://jason.diamond.name/weblog/2005/10/04/pypwsafe-release-1
    http://jason.diamond.name/weblog/2005/10/05/pypwsafe-0-0-2-with-setup-dot-py
"""
blowfish = None
try:
    if os.environ.get('NO_PYCRYPTO'):
        # disable PyCryptodome / PyCrypto via OS environment variable NO_PYCRYPTO
        # i.e. force use of pure python Blowfish
        raise ImportError
    # Try fast blowfish first
    # https://github.com/Legrandin/pycryptodome - PyCryptodome (safer/modern PyCrypto)
    # http://www.dlitz.net/software/pycrypto/ - PyCrypto - The Python Cryptography Toolkit
    import Crypto
    from Crypto.Cipher import Blowfish

    TheBlowfishCons = Blowfish.new
    TheBlowfishClass = type(TheBlowfishCons(b'1234', mode=Blowfish.MODE_ECB))

    def TheBlowfishCipher(password_bytes):
        return TheBlowfishCons(password_bytes, mode=Blowfish.MODE_ECB)

    # print('using PyCrypto')
    implementation = 'using PyCrypto ' + Crypto.__version__
    # TODO consider implementing support for pycryptodomex
except BaseException:
    try:
        import blowfish  # https://github.com/jashandeep-sohi/python-blowfish - currently py3 only :-(

        # TODO version number from blowfish
        implementation = 'using blowfish(pure python)'

        class PurePython3Blowfish:
            """Only implements ECB mode"""

            def __init__(self, password_key):
                """password_key is byte type and must be between 4 and 56 bytes long."""
                self.cipher = cipher = blowfish.Cipher(password_key)

            def decrypt(self, data_encrypted):
                data_decrypted = b"".join(self.cipher.decrypt_ecb(data_encrypted))
                return data_decrypted

            def encrypt(self, data):
                data_encrypted = b"".join(self.cipher.encrypt_ecb(data))
                return data_encrypted

        TheBlowfishCons = PurePython3Blowfish
        TheBlowfishClass = type(TheBlowfishCons(b'1234'))

        def TheBlowfishCipher(password_bytes):
            return TheBlowfishCons(password_bytes)

    except ImportError:
        if is_py3:
            raise
        import py2_blowfish as blowfish  # FIXME add py2 conditional

        implementation = 'using blowfish(pure python2)'
        TheBlowfishClass = blowfish.Blowfish
        TheBlowfishCons = blowfish.Blowfish
        TheBlowfishCipher = blowfish.Blowfish

if blowfish:
    implementation += ' ' + getattr(blowfish, '__version__', 'unknown version')

try:
    basestring  # only used to determine if parameter is a filename
except NameError:
    basestring = (
        str  # py3 - in this module, only used to determine if parameter is a filename
    )


# Workaround Ubuntu/Debian/Linux 64-bit array bug
x = array.array('L', [0])
if x.itemsize == 4:
    FMT_ARRAY_4BYTE = 'L'
    FMT_STRUCT_4BYTE = '<L'
else:
    x = array.array('I', [0])
    if x.itemsize == 4:
        FMT_ARRAY_4BYTE = 'I'
        FMT_STRUCT_4BYTE = '<L'
del x


def dump_bytes(s):
    """
    Poor mans hexdump (to stdio)
    """
    mycount = 0
    for c in s:
        sys.stdout.write('%02X' % ord(c))
        mycount = mycount + 1
        if mycount == 16:
            mycount = 0
            sys.stdout.write('\n')
    print


def swap_bytes(s):
    """
    Simple swap byte routine - Not actually used, here just in case
    """
    a = array.array(FMT_ARRAY_4BYTE, s)
    a.byteswap()
    return a.tostring()


class ChiIO(Exception):
    '''Base chi I/O exception'''


class BadPassword(ChiIO):
    '''Bad password exception'''


class UnsupportedFile(ChiIO):
    '''File not encrypted/not supported exception'''


def gen_random_string(length_of_str):
    """generate a string containing random characters of length length_of_str"""
    source_set = string.ascii_letters + string.digits + string.punctuation
    result = []
    for x in range(length_of_str):
        result.append(random.choice(source_set))
    return ''.join(result).encode('us-ascii')  # convert (Unicode) string to bytes


def CHI_cipher(password):
    if isinstance(password, TheBlowfishClass):
        cipher = password
    else:
        # Generate md5 sum of password, this is what is used as the encrypt key
        m = md5checksum()
        m.update(password)
        md5key = m.digest()
        cipher = TheBlowfishCipher(md5key)
    return cipher


def read_encrypted_file(fileinfo, password):
    """Reads a *.chi file encrypted by Tombo. Returns (8 bit) string containing plaintext.
    Raises exceptions on failure.

    fileinfo is either a filename (string) or a file-like object that reads binary bytes that be can read (caller is responsible for closing)
    password is a (byte) string, i.e. not Unicode type
    """
    if password is None:
        raise BadPassword('None passed in for password for file %r' % fileinfo)

    if isinstance(fileinfo, basestring):
        enc_filename = fileinfo
        in_file = open(enc_filename, 'rb')
    else:
        # assume it is a file-like object
        in_file = fileinfo
        ## TODO look up filename from object, file-likes usually have an attribute
        # enc_filename = in_file.name
        enc_filename = None

    # called version in CryptManager
    header = in_file.read(4)
    if header != b'BF01':
        raise UnsupportedFile('not a Tombo *.chi file')

    # read in 4 bytes and convert into an integer value
    ## NOTE may need to worry about byte swap on big-endian hardware
    # TODO do we need array lookup if we do not intend to byte swap???
    tmpbuf = in_file.read(4)
    # dump_bytes(tmpbuf)
    xx = array.array(FMT_ARRAY_4BYTE, tmpbuf)
    (enc_len,) = struct.unpack(FMT_STRUCT_4BYTE, xx)
    # TODO consider replacing above with:
    # (enc_len,) = struct.unpack(FMT_STRUCT_4BYTE, tmpbuf)

    enc_data = in_file.read()
    encbuf_len = len(enc_data)
    # print 'read in %d bytes, of that only %d byte(s) are real data' % (encbuf_len , enc_len)

    # Assume it is a plain text string (i.e. a byte string, not Unicode type)
    cipher = CHI_cipher(password)

    mycounter = encbuf_len
    decrypted_data = []
    second_pass = list(b"BLOWFISH")
    while mycounter >= 8:
        data = enc_data[:8]
        chipher = data
        enc_data = enc_data[8:]
        data = cipher.decrypt(data)
        ## based on debug code (and tombo specific additions to blowfish.c) in Tombo
        ## Tombo is using the base blowfish algorithm AND then applies more bit fiddling....
        ## performs bitwise exclusive or on decrypted text from blowfish and "BLOWFISH" (note this static gets modified....)
        for x in range(8):
            tmp_byte_a = data[x]
            tmp_byte_b = second_pass[x]
            if not is_py3:  # py2
                tmp_byte_a = ord(tmp_byte_a)
                tmp_byte_b = ord(tmp_byte_b)

            decrypted_data.append(tmp_byte_a ^ tmp_byte_b)
            second_pass[x] = chipher[x]
        mycounter = mycounter - 8
    ## there should be no bytes left after this.
    ## Ignore any remaining bytes (less than 8)?
    if mycounter > 0:
        # This should not happen if it did this may be a corrupted file
        # at present not handled, pending on bugs found here
        raise RuntimeError('ExtraBytesFound during decryption')
    if is_py3:
        decrypted_data = bytes(decrypted_data)
    else:  # py2
        decrypted_data = map(chr, decrypted_data)
        decrypted_data = b''.join(decrypted_data)
    """
    At this point decrypted_data contains:
        8 bytes of (unknown) random data
        16 bytes of an md5sum of the unencrypted data
        enc_len * bytes of unencrypted data
    
    But at this point we do not know if the password that was used was correct,
    the unencrypted data could be garbage!
    """

    # extract real text from supuriuos crap (24 bytes on from started of data)
    # loose spurious end use real data length we read earlier?
    unencrypted_str = decrypted_data[24:]
    unencrypted_str = unencrypted_str[:enc_len]

    m = md5checksum()
    m.update(unencrypted_str)
    decriptsum = m.digest()
    chi_md5sum = decrypted_data[8:]
    chi_md5sum = chi_md5sum[:16]

    if chi_md5sum == decriptsum:
        # passwords match, so data is valid
        return unencrypted_str
    else:
        # password did not match, data is bogus
        # raise exception WITH information such as filename, do not dump out password as that could be a security hole
        raise BadPassword(enc_filename)


def write_encrypted_file(fileinfo, password, plaintext):
    """Writes an encrypted *.chi file that could be read by Tombo. Parameter plaintext should be 8 bit string.
    Raises exceptions on failure (so caller is responsible for cleaning up incomplete out files).
    NOTE: if notes created with this routine are to be read in Tombo
    ensure to send in plaintext strings with Windows style newlines;
    i.e. '\x0D\x0A'. See dumb_unix2dos().

    fileinfo is either a filename (string) or a file-like object that writes binary bytes that be can written to (caller is responsible for closing)
    password is a (byte) string, i.e. not Unicode type

    """
    assert isinstance(
        plaintext, bytes
    ), 'Only support 8 bit plaintext (got %r). Encode first, see help(codecs).' % type(
        plaintext
    )

    plain_text = plaintext
    if isinstance(fileinfo, basestring):
        enc_filename = fileinfo
    else:
        # assume it is a file-like object
        enc_filename = None

    plain_text_len = len(plain_text)
    # print 'read in %d bytes' % plain_text_len

    m = md5checksum()
    m.update(plain_text)
    plain_text_md5sum = m.digest()

    # print "plain_text_md5sum"
    # dump_bytes(plain_text_md5sum)

    # Generate md5 sum of password, this is what is used as the encrypt key
    cipher = CHI_cipher(password)

    ## create new buffer that will be encrypted, contains:
    ##  8 bytes of random (if this is NOT random, then a plaintext+password will always create the SAME encrypted text)
    ##  16 bytes of md5 of plaintext
    ##  plain_text_len bytes of plaintext
    # str_to_encrypt = '12345678' + plain_text_md5sum + plain_text
    # enc_data = '12345678' + plain_text_md5sum + plain_text
    enc_data = gen_random_string(8) + plain_text_md5sum + plain_text

    mycounter = len(enc_data)
    encrypted_data = b''
    second_pass = b"BLOWFISH"
    while mycounter >= 8:
        data = enc_data[:8]

        ## based on debug code (and tombo specific additions to blowfish.c) in Tombo
        ## tombo is using the base blowfish alogrithm AND then applies more bit fiddling....
        ## performs bitwise exclusive or on decrypted text from blowfish and "BLOWFISH" (note this static gets modified....)
        plain = []
        for x in range(8):
            tmp_byte_a = data[x]
            tmp_byte_b = second_pass[x]
            if not is_py3:
                # py2
                tmp_byte_a = ord(tmp_byte_a)
                tmp_byte_b = ord(tmp_byte_b)
            plain.append(tmp_byte_a ^ tmp_byte_b)
        # print 'dec pass2 ', plain
        if is_py3:
            data = bytes(plain)
        else:  # py2
            data = map(chr, plain)
            data = b''.join(data)
        # print data
        # dump_bytes(data)

        enc_data = enc_data[8:]
        ##debug
        # first_byte = ord(data[0])
        # print 'raw : %x, %d' %(first_byte , first_byte )
        # dump_bytes(data)
        data = cipher.encrypt(data)

        # take encrypted block and shove into second pass but fiddler (really first pass when encrypting
        second_pass = []
        for x in range(8):
            second_pass.append(data[x])
        if is_py3:
            second_pass = bytes(second_pass)
        else:
            second_pass = ''.join(second_pass)

        ##debug
        # first_byte = ord(data[0])
        # print 'encrypted : %x, %d' %(first_byte , first_byte )
        # print ""
        encrypted_data = encrypted_data + data
        mycounter = mycounter - 8
    ## there maybe a few odd bytes left after this (less than 8). Take then and put with random bytes into an 8 byte block and encrypt that
    if mycounter > 0:
        # take  last few bytes "data"
        tmp_buf = []
        for x in range(mycounter):
            tmp_buf.append(enc_data[x])
        if is_py3:
            data = bytes(tmp_buf)
        else:
            data = ''.join(tmp_buf)

        # Tombo bit fiddling
        # NOTE in Tobo the "fake" padding bytes at the end are not bit fiddled with
        plain = []
        for x in range(mycounter):
            tmp_byte_a = data[x]
            tmp_byte_b = second_pass[x]
            if not is_py3:  # is py2
                tmp_byte_a = ord(tmp_byte_a)
                tmp_byte_b = ord(tmp_byte_b)
            plain.append(tmp_byte_a ^ tmp_byte_b)
        if is_py3:
            data = plain
        else:
            data = map(chr, plain)

        # pad the end few bytes so that blowfish can be applied
        # just take "garbage" from begnning of (last/previously) encrypted block
        # NOTE this differs from Tombo which takes the garbage from the end of the previously encrypted block
        for x in range(8 - mycounter):
            data.append(data[x])

        if is_py3:
            data = bytes(plain)
        else:  # is py2
            data = b''.join(data)

        # Now encrypt
        data = cipher.encrypt(data)
        encrypted_data = encrypted_data + data

    ## file IO section
    if enc_filename is not None:
        out_file = open(enc_filename, 'wb')
    else:
        # assume it is a file-like object
        out_file = fileinfo

    # called version in tombo's CryptManager
    header = b'BF01'

    out_file.write(header)

    # write out 4 bytes - integer value containing unencrypted length of data
    # write out plaintext length
    out_file.write(struct.pack(FMT_STRUCT_4BYTE, plain_text_len))

    # write out encrypted data
    out_file.write(encrypted_data)

    if enc_filename is not None:
        # i.e. we opened the file so we need to close it
        out_file.close()


def dumb_unix2dos(in_str):
    """In-efficient but simple unix2dos string conversion
    convert '\x0A' --> '\x0D\x0A'
    """
    return in_str.replace('\x0A', '\x0D\x0A')


## Consider using filelike from http://cheeseshop.python.org/pypi/filelike/
class ChiAsFile(object):
    """does not really honor seek(), etc. only read/write"""

    def __init__(self, fileptr, password, mode=None):
        self._fileptr = fileptr
        self._password = password
        self._bufferedfileptr = FakeFile()
        mode = mode or 'r'
        if 'w' in mode:
            self._mode = 'w'
        elif '+' in mode:
            self._mode = '+'  # read and write
        elif 'r' in mode:
            self._mode = 'r'
        else:
            # TODO "a" append mode (+), implications for seek()?
            raise NotImplemented('mode=%r' % mode)
        if self._mode in ('r', '+'):
            self._read_from_file()  # FIXME make this lazy, rather than at init time

    def __getattr__(self, attr):
        if self.__dict__.has_key(attr):
            return self.__dict__[attr]
        else:
            return getattr(self._bufferedfileptr, attr)

    def _read_from_file(self):
        # TODO this may be the start of allowing read and write support in the same session
        plain_text = read_encrypted_file(self._fileptr, self._password)
        self._bufferedfileptr = FakeFile(plain_text)

    def read(self, size=None):
        if self._mode == 'w':
            raise IOError(
                'file was write, and then read issued. read and write are mutually exclusive operations'
            )
        # do we need this if?
        if size is None:
            return self._bufferedfileptr.read()
        else:
            return self._bufferedfileptr.read(size)

    def seek(self, offset):  # FIXME `whence` support
        return self._bufferedfileptr.seek(offset)

    def write(self, str_of_bytes):
        if self._mode == 'r':
            raise IOError(
                'file was read, and then write issued. read and write are mutually exclusive operations'
            )
        return self._bufferedfileptr.write(str_of_bytes)

    def close(self, *args, **kwargs):
        ## do we need to call this in __del__?
        if self._mode != 'r':
            # i.e writable file
            plain_text = self._bufferedfileptr.getvalue()
            if self._mode == '+':
                self._fileptr.seek(0)
                self._fileptr.truncate()
            write_encrypted_file(self._fileptr, self._password, plain_text)
        # self._fileptr.close() # is this right?
        self._bufferedfileptr.close()
        ## TODO disallow more writes/closes....


def demo_test():
    """Examples of use with some error handling"""
    print("tombo test example")

    plain_text = b"""12345678"""
    enc_fname = 'chi_io_test1.chi'
    mypassword = b'testing'

    print('Write encrypted file to', enc_fname)
    write_encrypted_file(enc_fname, mypassword, plain_text)
    try:
        print('Reading encrypted file', enc_fname)
        plain_str = read_encrypted_file(enc_fname, mypassword)
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except BadPassword as info:
        print("bad password used")
        print(info)
    except UnsupportedFile as info:
        print("file was not encrypted or is not supported")
        print(info)
    print('\n***************************\n')

    plain_text = b"""Line 1
of a simple text file.
"""
    enc_fname = 'chi_io_test.chi'
    mypassword = b'testing'

    print('Write multiline encrypted file to', enc_fname)
    write_encrypted_file(enc_fname, mypassword, plain_text)
    try:
        print('Reading encrypted file', enc_fname)
        plain_str = read_encrypted_file(enc_fname, mypassword)
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except BadPassword as info:
        print("bad password used")
        print(info)
    except UnsupportedFile as info:
        print("file was not encrypted or is not supported")
        print(info)
    print('\n***************************\n')
    mypassword = b'bad password'
    try:
        print('Reading encrypted file with bad password', enc_fname)
        plain_str = read_encrypted_file(enc_fname, mypassword)
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except BadPassword as info:
        print("bad password used")
        print(info)
    except UnsupportedFile as info:
        print("file was not encrypted or is not supported")
        print(info)
    print('\n***************************\n')

    enc_fname = 'delete_me.txt'
    mypassword = b'testing'
    myfile = open(enc_fname, 'w')
    myfile.write('hello world')
    myfile.close()
    try:
        print('Reading non-encrypted file', enc_fname)
        plain_str = read_encrypted_file(enc_fname, mypassword)
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except BadPassword as info:
        print("bad password used")
        print(info)
    except UnsupportedFile as info:
        print("file was not encrypted or is not supported")
        print(info)
    print('\n***************************\n')

    enc_fname = 'doesnotexist.chi'
    mypassword = b'testtest'
    try:
        print('Reading Non-existent encrypted file', enc_fname)
        plain_str = read_encrypted_file(enc_fname, mypassword)
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except BadPassword as info:
        print("bad password used")
        print(info)
    except UnsupportedFile as info:
        print("file was not encrypted or is not supported")
        print(info)
    except IOError as info:
        print("Some kind of IO error, probably a missing file")
        print(info)
    print('\n***************************\n')

    plain_text = u'123\N{POUND SIGN}'
    enc_fname = 'unicode.chi'
    mypassword = b'testing'

    try:
        print('Write encrypted file to', enc_fname)
        write_encrypted_file(enc_fname, mypassword, plain_text)
    except AssertionError as info:
        print("assert error, probably tried to feed in Unicode")
        print(info)
    print('\n***************************\n')

    plain_text = u'123\N{POUND SIGN}'
    enc_fname = 'unicode.chi'
    mypassword = b'testing'

    try:
        print('Write encrypted file with unicode to', enc_fname)

        plain_text = plain_text.encode(
            'utf-8'
        )  ## convert to binary string, could be UTF-16, etc
        write_encrypted_file(enc_fname, mypassword, plain_text)

        plain_str = read_encrypted_file(enc_fname, mypassword)
        plain_str = plain_str.decode('utf-8')  ## convert to Unicode string
        print('--------- Decrypted data ---------')
        print(plain_str)
        print('-------------- End ---------------')
    except AssertionError as info:
        print("assert error, probably tried to feed in Unicode")
        print(info)
    print('\n***************************\n')

    os.remove('chi_io_test.chi')
    os.remove('chi_io_test1.chi')
    os.remove('unicode.chi')

    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('argv', argv)
    if len(argv) >= 2:
        print('argv[1]', argv[1])

    if is_py3:
        global raw_input
        raw_input = input
    try:
        enc_fname = argv[1]
    except IndexError:
        enc_fname = None

    if enc_fname == 'demo_test':
        return demo_test()

    if enc_fname:
        # default to Decrypt when a filename specified
        do_what = 'd'
    else:
        do_what = raw_input(
            'Encrypt (e) or Decrypt (d), anything else run demo test?: '
        )

        print("do_what", do_what, len(do_what))

        if do_what != 'e' and do_what != 'd':
            return demo_test()

    if not enc_fname:
        enc_fname = raw_input('enter in encrypted filename (e.g. test.chi): ')

    import getpass

    mypassword = getpass.getpass("Password:")
    mypassword = mypassword.encode('us-ascii')

    if do_what == 'e':
        plain_fname = raw_input('enter in plain text filename (e.g. test.txt): ')
        in_file = open(plain_fname, 'rb')
        plain_text = in_file.read()
        in_file.close()
        print('Write encrypted file to', enc_fname)
        write_encrypted_file(enc_fname, mypassword, plain_text)
    else:  ## do_what == 'd':
        try:
            print('Reading encrypted file', enc_fname)
            plain_str = read_encrypted_file(enc_fname, mypassword)
            file_encoding = 'utf-8'  # assume! safe thing (avoid error) would be latin1 but would then have display issues
            file_encoding = 'latin1'  # do not error, but may display incorrectly
            plain_str = plain_str.decode(file_encoding)
            print('--------- Decrypted data ---------')
            print(plain_str)
            print('-------------- End ---------------')
        except BadPassword as info:
            print("bad password used")
            print(info)
        except UnsupportedFile as info:
            print("file was not encrypted or is not supported")
            print(info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
