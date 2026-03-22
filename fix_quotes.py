import glob
import os

print("Fixing files:", glob.glob('src/*.py'))
for f in glob.glob('src/*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        data = file.read()
    
    # Replace the escaped quotes with proper python docstring quotes
    data = data.replace('\\"\\"\\"', '"""')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(data)
print("Done fixing.")
