import sys


class Console:
    """
    A helper class for displaying messages on the console (stderr).
    """

    Black = '\033[30m'
    BlackBackground = '\033[40m'
    Blue = '\033[94m'
    Green = '\033[92m'
    GreenBackground = '\033[42m'
    Yellow = '\033[93m'
    YellowBackground = '\033[103m'
    Red = '\033[91m'
    RedBackground = '\033[41m'
    Grey = '\033[37m'
    Reset = '\033[0m'

    @staticmethod
    def title(title):
        print('%s%s%s' % (Console.Blue, title, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def success(message):
        print('%s%s%s' % (Console.Green, message, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def error(message):
        print('%s%sError%s%s: %s%s' %
              (Console.RedBackground, Console.Black, Console.Reset,
               Console.Grey, message, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def warning(message):
        print('%s%sWarning%s%s: %s%s' %
              (Console.YellowBackground, Console.Black, Console.Reset,
               Console.Grey, message, Console.Reset),
              file=sys.stderr)

    @staticmethod
    def info(message):
        print(message, file=sys.stderr)
