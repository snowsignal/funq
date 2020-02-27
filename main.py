from sys import argv


def run_application(arg_list: list) -> None:
    for i in range(0, len(arg_list)-1):
        arg = arg_list[i]



if __name__ == "__main__":
    args = argv[1:]
    run_application(args)
