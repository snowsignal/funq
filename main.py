from sys import argv


class CommandLineInterface:
    def __init__(self, args=None):
        self.file_to_open = None
        self.output_folder = "./funq_build"
        self.region_file_map = {}
        self.regions_to_stdout = []
        self.save_all_by_default = True
        if args is None:
            self.args = []
        else:
            self.args = args

        self.should_exit = self._load()

    def should_exit(self):
        return self.should_exit

    def print_help(self):
        print("""
Usage: funq <INPUT> [OPTIONS]
where <INPUT> is a valid relative or absolute filename.
Options:
-h, --help                                     -> Prints this help screen
-l <PATH>, --location <PATH>                   -> Specifies a location to output files to 
                                                   (default is the folder 'funq_build')
-o <REGION> <FILE>, --output <REGION> <FILE>   -> Specifies what a compiled region should be saved as.
--stdout <REGION>                              -> Outputs compiled region with name <REGION> directly to STDOUT, in addition to
                                                    saving it to a file.
--no-default-save                              -> Tells the compiler to not output any files by default, besides the ones
                                                    specifically defined. 
""")

    def interface_error(self, msg):
        print("--- ERROR ---")
        print(msg)
        print("-------------")

    def compiler_error(self, msg):
        print("--- COMPILATION ERROR ---")
        print(msg)
        print("-------------------------")

    def _load(self):
        if len(self.args) == 0:
            self.interface_error("No input file specified\nUse 'funq -h' for help.")
            return True

        def get_next_or_err(i, args, expected=""):
            if len(args) - 1 <= i:
                self.interface_error("Unexpected end of arguments: expected <" + expected + ">")
                return False, None
            else:
                return True, args[i+1]
        skip_next = 0
        for (i, arg) in enumerate(self.args):
            if i == 0 and arg != "-h" and arg != "--help":
                # This HAS to be the input file
                self.file_to_open = arg
                # TODO: Verify file is valid
                continue
            if skip_next > 0:
                skip_next -= 1
                continue
            if arg == "-h" or arg == "--help":
                self.print_help()
                return True
            elif arg == "--no-default-save":
                self.save_all_by_default = False
            elif arg == "-l" or arg == "--location":
                skip_next = 1
                if get_next_or_err(i, self.args, expected="PATH")[0]:
                    f = get_next_or_err(i, self.args)[1]
                    self.output_folder = f
                else:
                    return True
            elif arg == "-o" or arg == "--output":
                skip_next = 2
                if get_next_or_err(i, self.args, expected="REGION")[0] and get_next_or_err(i+1, self.args, expected="FILE")[0]:
                    r = get_next_or_err(i, self.args)[1]
                    f = get_next_or_err(i+1, self.args)[1]
                    self.region_file_map[r] = f
                else:
                    return True
            elif arg == "--stdout":
                skip_next = 1
                if get_next_or_err(i, self.args, expected="REGION")[0]:
                    r = get_next_or_err(i, self.args)[1]
                    self.regions_to_stdout.append(r)
                else:
                    return True
            else:
                self.interface_error("Unexpected argument '" + arg + "'")
                return True
        return False




    def main(self):
        # Main function for the compiler

        # Step One: Open the input file
        file = open(self)

def run_application(arg_list: list) -> None:
    command_line_interface = CommandLineInterface(args=arg_list)



if __name__ == "__main__":
    a = argv[1:]
    run_application(a)
