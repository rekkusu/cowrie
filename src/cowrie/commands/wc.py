
import getopt

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound

commands = {}

class command_wc(HoneyPotCommand):

    def start(self):
        try:
            optlist, args = getopt.gnu_getopt(self.args, 'cmlLw', ['help', 'bytes', 'chars', 'lines', 'max-line-length', 'words', 'version'])
        except getopt.GetoptError as err:
            self.errorWrite("wc: invalid option -- '{}'\nTry 'wc --help' for more information.\n".format(err.opt))
            self.exit()
            return

        self.mode = []

        for o, a in optlist:
            if o in ('--help'):
                self.help()
                self.exit()
                return

            if o in ('-c', '--bytes'):
                self.mode.append('bytes')
            if o in ('-m', '--chars'):
                self.mode.append('chars')
            if o in ('-l', '--lines'):
                self.mode.append('lines')
            if o in ('-w', '--words'):
                self.mode.append('words')

        # default options
        if len(self.mode) == 0:
           self.mode = ['lines', 'words', 'bytes']

        if self.input_data is not None:
            if not hasattr(self, 'buffer'):
                self.buffer = ''
            self.buffer += self.input_data
            log.msg(eventid='cowrie.session.input',
                    realm='wc',
                    input=self.input_data,
                    format='INPUT (%(realm)s): %(input)s')
        else:
            for arg in args:
                pname = self.fs.resolve_path(arg, self.protocol.cwd)

                if self.fs.isdir(pname):
                    self.errorWrite('wc: {}: Is a directory\n'.format(arg))
                    continue

                try:
                    contents = self.fs.file_contents(pname)
                    if contents:
                        self.word_count(contents, pname)
                    else:
                        raise FileNotFound
                except FileNotFound:
                    self.errorWrite('wc: {}: No such file or directory\n'.format(arg))
            self.exit()

    def word_count(self, input, fname=''):
        count = []
        if 'lines' in self.mode:
            count.append(len(input.strip('\n').split('\n')))

        if 'words' in self.mode:
            lines = input.decode('utf-8').split('\n')
            c = 0
            for line in lines:
                c += len(filter(lambda w: len(w) > 0, line.split(' ')))
            count.append(c)

        if 'chars' in self.mode:
            count.append(len(input.decode('utf-8')))

        if 'bytes' in self.mode:
            count.append(len(input))

        pad = len(str(count[-1]))

        for i in range(len(count)):
            if i > 0:
                self.write(' ')

            self.write(str(count[i]).rjust(pad))

        if fname != '':
            self.write(' ' + fname)

        self.write('\n')

    def lineReceived(self, line):
        log.msg(eventid='cowrie.session.input',
                realm='wc',
                input=line,
                format='INPUT (%(realm)s): %(input)s')

        if not hasattr(self, 'buffer'):
            self.buffer = ''

        self.buffer += line + '\n'

    def pipeReceived(self, line):
        log.msg(eventid='cowrie.session.input',
                realm='wc',
                input=line,
                format='PIPE (%(realm)s): %(input)s')

        if not hasattr(self, 'buffer'):
            self.buffer = ''

        self.buffer += line

    def exit(self):
        if hasattr(self, 'buffer'):
            self.word_count(self.buffer)

        HoneyPotCommand.exit(self)

    def handle_CTRL_D(self):
        self.exit()

    def help(self):
        self.write(
            """Usage: wc [OPTION]... [FILE]...
  or:  wc [OPTION]... --files0-from=F
Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified.  A word is a non-zero-length sequence of
characters delimited by white space.

With no FILE, or when FILE is -, read standard input.

The options below may be used to select which counts are printed, always in
the following order: newline, word, character, byte, maximum line length.
  -c, --bytes            print the byte counts
  -m, --chars            print the character counts
  -l, --lines            print the newline counts
      --files0-from=F    read input from the files specified by
                           NUL-terminated names in file F;
                           If F is - then read names from standard input
  -L, --max-line-length  print the maximum display width
  -w, --words            print the word counts
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
Full documentation at: <http://www.gnu.org/software/coreutils/wc>
or available locally via: info '(coreutils) wc invocation'"""
        )


commands['/usr/bin/wc'] = command_wc
commands['wc'] = command_wc
