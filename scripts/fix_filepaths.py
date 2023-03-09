import os
import re

processed_repos_dir = '../processed_repos'

# Recursively get a list of all the JSON files in the processed repos directory
json_files = [os.path.join(dp, f)
              for dp, dn, filenames in os.walk(processed_repos_dir)
              for f in filenames if f.endswith('.json')]

# Replace the file paths in each JSON file
for json_file in json_files:
    with open(json_file, 'r+') as f:
        data = f.read()
        # Use regex to replace the file paths with the modified versions
        data = re.sub(r'"filepath": "(../../../)*(.+?)"',
                      lambda m: f'"filepath": "{m.group(2)}"',
                      data)
        f.seek(0)
        f.write(data)
        f.truncate()
