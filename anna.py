#Need to wrap a bit of this in a try statement in order to tell me im being dumb and not adding flags to query
#also *ideally* want to be able to run anna.py from book.sh without hardcoding the location of the file to make everything more portable
#aside from that definitely need like a lot more error handling and basic instructions on how to use this
#current handling of flags is... definitely something.

#do excuse the naming conventions. I'm mostly used to java, but I'm a bit tired as of writing this. This was mostly done to learn a bit of python and bash,
#and definitely took a lot of time to figure out what I was doing with awk and sed.

import requests, json, random, sys, textwrap, subprocess, ast, html
#from bs4 import BeautifulSoup
#improved error handling through BeautifulSoup coming soon, to a theater near you

filename = ""
query = "" 
beenRenamed = False #unfortunately I have not yet implemented renaming via arguments, but the bash script has a fair bit of work put in to name it 
firstQuery = True   #in a way that makes a bit of sense.


idx = 1
expecting_filename = False 

while idx < len(sys.argv):
    arg = sys.argv[idx]

    if arg == "-r":
        if not beenRenamed: 
            expecting_filename = True
            beenRenamed = True
        else:
            if firstQuery:
                query = arg
                firstQuery = False
            else:
                query += '+' + arg
        idx += 1
        continue
    if expecting_filename:
        filename = arg
        expecting_filename = False 
        idx += 1
        continue
    if firstQuery:
        query = arg
        firstQuery = False
    else:
        query += '+' + arg
    idx += 1

#print("Filename:", filename)
#print("Query:", query)
command = 'wget --user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0" \'https://annas-archive.org/search?index=&page=1&q='+query+'&display=&lang=en&sort=\' -O html.html'
#print("long waits are due to anna's archive being slow as shit. either that or my internet, and we should leave that topic alone.")
try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True) #shelling out. probably a better way to do this. I'll get there


except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    print(f"Return code: {e.returncode}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
except FileNotFoundError:
    print("Error: 'wget' command not found. Make sure it's installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


#I suggest those with sensitive eyes read no further than this comment. My very hardcoded script has practically zero error handling as is entirely hardcoded.
#In fact, it was only after I started piping everything into fzf in the bash script that I realized the secondary section of results requires special handling.
hashes = ""
hashLine = 0
start = 0
end = 0
search = "aarecord-list"

with open(r'html.html', 'r') as fp:
    matches = 0
    lines = fp.readlines()
    for line in lines:
        if matches == 0:
            if line.find(search) != -1:
                matches+=1
                start = lines.index(line)
        elif matches == 1:
            if line.find(search) != -1:
                matches+=1
                end = lines.index(line)
    with open('temp.html', 'w') as op:
        for i in range(start,end + 1):
            op.write(lines[i])
        op.close()
    fp.close()


titlesArray = []
hashArray = []
metadataArray = []
publisherArray = []
authorArray = []
with open(r'temp.html', 'r') as title:
    lines = title.readlines()
    for line in lines:
        if line.find('font-bold') != -1:
            tResult = str(lines[lines.index(line)])
            titlesArray.append(tResult[119:len(tResult)-6])
        if(line.find('<!--        <a href=\"/md5/')) != -1: #special handling here. Disgusting, im aware. youll see me use unescape one time.
            hResult = str(lines[lines.index(line)])
            hashArray.append(hResult[26:58])
        elif(line.find('/md5/')) != -1:
            hResult = str(lines[lines.index(line)])
            hashArray.append(hResult[22:54])
        if(line.find('text-gray-500')) != -1:
            mResult = str(lines[lines.index(line)])
            metadataArray.append(mResult[91:len(mResult)-7])
        if(line.find('max-lg:text-xs')) != -1:
            pResult = str(lines[lines.index(line)])
            publisherArray.append(pResult[81:len(pResult)-7])
        if(line.find('max-lg:text-sm')) != -1:
            aResult = str(lines[lines.index(line)])
            authorArray.append(aResult[113:len(aResult)-7])



































class BookEntry:
    def __init__(self, md5_hash_line, title_line, metadata_line, publisher_info_line, author_line):
        self.md5_hash = md5_hash_line
        self.title = title_line
        self.metadata_raw = metadata_line
        self.publisher_info_raw = publisher_info_line
        self.author = author_line



all_book_data_zipped = zip(hashArray, titlesArray, metadataArray, publisherArray, authorArray)
book_objects = []

for md5, title, metadata, publisher, author in all_book_data_zipped:
    book = BookEntry(md5, title, metadata, publisher, author)
    book_objects.append(book)

#print(json.dumps([entry.to_dict() for entry in book_objects], indent=2))















print("--- Printing Raw Book Data ---") #this is the least terrible part of the script, i would say
                                        #in no way perfect, and no way of specifying how many results the user wants displayed, but functional.
for i, book in enumerate(book_objects):
    if i >= 20:
        break
    print(f"\n--- Book {i+1} ---")
    print(f"MD5: {book.md5_hash}")
    print(f"Title: {book.title}")
    print(f"Metadata: {book.metadata_raw}")
    if str(book.publisher_info_raw)!="":
        print(f"Publisher: {book.publisher_info_raw}")
    if str(book.author) !="":
        print(f"Author: {html.unescape(book.author)}")
