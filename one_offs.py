# feed this script a plain text file with a resource_id on each line
# \n line separators, no other text at all
#
# ~$ python3 one_offs.py MY_CSPACE_INSTANCE resource_ids.txt
#
import asyncio
import concurrent.futures
import sys

import main

cspace_instance = sys.argv[1]
id_list_file = sys.argv[2]

def do_it():
    with open(id_list_file,'r') as f:
        for resource_id in f:
            print(resource_id)
            result = asyncio.run(main.push_image(cspace_instance,resource_id.rstrip()))
            print(result)

if __name__ == "__main__":
    do_it()
