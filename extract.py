import os
from bs4 import BeautifulSoup as bs
import json

def extract_list_file(file_name):
    # os.chdir('/html')
    files = os.listdir()
    list_comments = list()

    count = 1
    for file in files:
        if (file.split('.')[1] == 'html'):
            print("Read file ",count,'/',str(len(files))+": ", file)
            count+=1

            f = open(file, 'r')
            soup = bs(f.read())
            comments = soup.find_all("div", {"data-sigil": "comment-body"})

            for i in comments:
                list_comments.append(i.text)
            print("Length list: ", len(list_comments))

    with open('./' + file_name + '.json', 'a', encoding='utf-8') as file:
        file.write(json.dumps(list_comments, ensure_ascii=False).encode('utf-8').decode())

if __name__ == '__main__':
    extract_list_file('comments')