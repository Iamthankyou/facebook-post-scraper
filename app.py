from scraper import read_comment_mobile_post
import argparse

parser = argparse.ArgumentParser(description="Facebook Page Scraper")
required_parser = parser.add_argument_group("required arguments")
required_parser.add_argument('-page', '-p', help="Facebook page", required=False)
required_parser.add_argument('-list', '-l', help="List facebook page", required=False)

args = parser.parse_args()

if args.list:
    file = open(args.list, "r")
    line = file.readline()
    while line:
        print("Page: ", line)
        read_comment_mobile_post(line)
        print("End: ", line)
        line = myfile.readline()
    file.close()
else:
    page = args.page
    read_comment_mobile_post(page)


