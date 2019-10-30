import sys
import winreg
from argparse import ArgumentParser


def search(needle):
    found = False
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer\\UserData", access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as userDataParentHandle:
        for userDataIndex in range(0, winreg.QueryInfoKey(userDataParentHandle)[0]):
            user = winreg.EnumKey(userDataParentHandle, userDataIndex)
            with winreg.OpenKey(userDataParentHandle, user) as userDataHandle:
                with winreg.OpenKey(userDataHandle, "Components") as componentsParentHandle:
                    for componentIndex in range(0, winreg.QueryInfoKey(componentsParentHandle)[0]):
                        with winreg.OpenKey(componentsParentHandle, winreg.EnumKey(componentsParentHandle, componentIndex)) as componentHandle:
                            for valueIndex in range(0, winreg.QueryInfoKey(componentHandle)[1]):
                                valueName, valueData = winreg.EnumValue(componentHandle, valueIndex)[0:2]
                                if needle.casefold() in valueData.casefold():
                                    with winreg.OpenKey(userDataHandle, "Products\\" + valueName + "\\InstallProperties") as propertiesHandle:
                                        if not found:
                                            found = True
                                        else:
                                            print()

                                        print("File: " + valueData)
                                        print("Product: " + winreg.QueryValueEx(propertiesHandle, "DisplayName")[0])
                                        print("Install user: " + user)
                                        print("Cached installer: " + winreg.QueryValueEx(propertiesHandle, "LocalPackage")[0])

    if not found:
        print('No file path containing "{}" was found in any installed package.'.format(needle))


def search_command(opts):
    return search(opts.pattern)


def create_parser(prog_name):
    parser = ArgumentParser(prog=prog_name)
    sp = parser.add_subparsers(title='commands', description='valid commands:')
    search = sp.add_parser('search', help='Search for a file within an installed component')
    search.add_argument('pattern', help='Name of the file')
    search.set_defaults(func=search_command)
    return parser


def main():
    parser = create_parser(sys.argv[0])
    opts = parser.parse_args(sys.argv[1:])
    opts.func(opts)


if __name__ == '__main__':
    main()
