#! /usr/bin/python3
# -*- coding: utf-8 -*-

'''
      Copyright 2016,王思远 <darknightghost.cn@gmail.com>
      This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
      You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os
import sys

class SubProc:
    def __init__(self, path, argv, encoding = 'utf-8'):
        self.path = path
        self.argv = argv
        self.encoding = encoding

        #Get file descriptors
        self.stdinFd = sys.stdin.fileno()
        self.stdoutFd = sys.stdout.fileno()
        self.stderrFd = sys.stderr.fileno()
        
        #Create pipe
        self.parentIn, self.childStdout = os.pipe()
        self.childStdin, self.parentOut = os.pipe()

        pid = os.fork()
        if pid == 0:
            self.is_child()

        else:
            self.child_id = pid
            self.is_parent()

        self.buffer = ""

    def is_child(self):
        os.close(self.parentIn)
        os.close(self.parentOut)
        os.dup2(self.childStdin, self.stdinFd)
        os.dup2(self.childStdout, self.stdoutFd)
        os.dup2(self.childStdout, self.stderrFd)

        os.execv(self.path, self.argv)

    def is_parent(self):
        os.close(self.childStdin)
        os.close(self.childStdout)

    def read(self):
        bs = os.read(self.parentIn, 1024)

        ret = self.buffer + bs.decode(encoding = self.encoding,
                errors = 'ignore')

        self.buffer = ""
        return ret

    def read_until(self, string):
        if string in self.buffer:
            index = self.buffer.index(string)
            ret = self.buffer[: index] = string
            self.buffer = self.buffer[index + len(self.buffer): ]
            return ret

        str_len = len(string)
        cmp_str = self.buffer[-str_len :]

        while True:
            bs = os.read(self.parentIn, 1024)
            s = self.buffer + bs.decode(encoding = self.encoding,
                errors = 'ignore')
            cmp_str += s
            self.buffer += s

            if string in cmp_str:
                index = self.buffer.index(string)
                ret = self.buffer[: index] = string
                self.buffer = self.buffer[index + len(self.buffer): ]
                return ret

            cmp_str = cmp_str[-str_len :]


    def write(self, string):
        os.write(self.parentOut, string.encode(encoding = self.encoding,
            errors = 'ignore'))

    def read_line(self):
        return self.read_until('\n')

    def __del__(self):
        os.close(self.parentIn)
        os.close(self.parentOut)
        try:
            os.kill(self.child_id, 9)

        except Exception:
            pass

        os.wait()
