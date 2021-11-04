from scraper import *
import re

f = open('saved.txt','r')
line = f.readline()
g = open('tmp.txt','w')
while line:
    g.writelines(re.search('fbid=[0-9]+',line).group(0).split('=')[1]+'\n')
    line = f.readline()

    
