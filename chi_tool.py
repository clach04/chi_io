#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
"""Command line tool to encrypt/decrypt Tombo CHI Blowfish files
"""

import getpass
import os
from optparse import OptionParser
import sys

import chi_io


is_py3 = sys.version_info >= (3,)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if is_py3:
        stream_encoding = 'utf-8'  # FIXME hard coded

    verbose = True
    verbose = False
    if verbose:
        print(sys.version)
        print(chi_io.implementation)

    usage = "usage: %prog [options] in_filename"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-o", "--output", dest="out_filename", default='-',
                        help="write output to FILE", metavar="FILE")
    parser.add_option("-d", "--decrypt", action="store_true", dest="decrypt", default=True,
                        help="decrypt in_filename")
    parser.add_option("-e", "--encrypt", action="store_false", dest="decrypt",
                        help="encrypt in_filename")
    parser.add_option("-c", "--codec", help="File encoding", default='utf-8')
    parser.add_option("-p", "--password", help="password, if ommited but OS env CHI_PASSWORD is set use that, if missing prompt")
    parser.add_option("-P", "--password_file", help="file name where password is to be read from, trailing blanks are ignored")
    parser.add_option("-v", "--verbose", action="store_true")
    parser.add_option("-s", "--silent", help="if specified do not warn about stdin using", action="store_false", default=True)
    (options, args) = parser.parse_args(argv[1:])
    #print('%r' % ((options, args),))
    verbose = options.verbose
    if verbose:
        print(sys.version)
        print(chi_io.implementation)

    def usage():
        parser.print_usage()

    """
    if not args:
        parser.print_usage()
    """
    try:
        in_filename = args[0]
    except IndexError:
        # no filename specified so default to stdin
        in_filename = '-'

    if options.password_file:
        f = open(options.password_file, 'rb')
        password_file = f.read()
        f.close()
        password_file = password_file.strip()
    else:
        password_file = None
    password = options.password or password_file or os.environ.get('CHI_PASSWORD') or getpass.getpass("Password:")
    decrypt = options.decrypt
    out_filename = options.out_filename
    note_encoding = options.codec

    if not isinstance(password, bytes):
        password = password.encode('us-ascii')

    if in_filename == '-':
        if is_py3:
            in_file = sys.stdin.buffer
        else:
            in_file = sys.stdin
        if options.silent:
            sys.stderr.write('Read in from stdin...')
            sys.stderr.flush()
        # TODO for py3 handle string versus bytes
    else:
        in_file = open(in_filename, 'rb')
    if out_filename == '-':
        if is_py3:
            out_file = sys.stdout.buffer
        else:
            out_file = sys.stdout
        # handle string versus bytes....?
    else:
        out_file = open(out_filename, 'wb')

    failed = True
    try:
        if decrypt:
            #import pdb ; pdb.set_trace()
            plain_str = chi_io.read_encrypted_file(in_file, password)
            if is_py3:
                # encode to stdout encoding  TODO make this optional, potentially useful for py2 too
                plain_str = plain_str.decode(note_encoding).encode(stream_encoding)
            out_file.write(plain_str)
        else:
            # encrypt
            plain_text = in_file.read()
            chi_io.write_encrypted_file(out_file, password, plain_text)
            failed = False
    except chi_io.BadPassword as info:
        print("bad password used. %r" % (info,))
    except chi_io.UnsupportedFile as info:
        print("file was not encrypted or is not supported file %r" % (info,))
    finally:
        if in_file != sys.stdin:
            in_file.close()
        if out_file != sys.stdout:
            out_file.close()

    if failed:
        return 1


    return 0


if __name__ == "__main__":
    sys.exit(main())
