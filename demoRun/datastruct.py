import json

with open('output.json', 'r', encoding='utf-8') as f1, open('chapters_dvc_test.json', 'r', encoding='utf-8') as f2:
    file1 = json.load(f1)
    file2 = json.load(f2)

converted = {}
for key in file1.keys():
    if key in file2:
        chapters = []
        for i, (start, end) in enumerate(file2[key]["timestamps"]):
            chapter_title = file2[key]["sentences"][i]
            chapters.append(f"[chapter : {chapter_title} {start:.2f} {end:.2f}]")
        
        converted[key] = "start of data " + " \n".join(chapters) + " \nend of data"

with open('converted_file.json', 'w', encoding='utf-8') as f_out:
    json.dump(converted, f_out, indent=4)

print("Conversion completed! Check converted_file.json")
