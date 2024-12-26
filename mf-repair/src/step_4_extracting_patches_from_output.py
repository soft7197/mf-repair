import re
import json

def extract_fixed_method(output):
    pattern = r"```java(.*?)```"
    matches = re.findall(pattern, output, re.DOTALL)  # re.DOTALL allows . to match newlines
    return matches

def get_method_name(str):
    pattern = r"\b(?:public|private|protected|static|final|synchronized|native|abstract|default|strictfp)*\s+" \
            r"(?:<[^>]+>\s+)?(?:[\w\[\]<>]+)\s+([a-zA-Z_$][a-zA-Z\d_$]*)\s*\("  
    match = re.search(pattern, str)
    if match:
        return match.group(1)
    return ""

def main():
    with open ("/Users/aslan/Desktop/MFRepair_ubuntu/resources/defects4jv1_mf_with_gptspatch.json", "r") as file:
       data=json.load(file)
    try:
        for bug_id in data:
            n = 0
            for method in data[bug_id]['functions']:
                if 'patches' in method:
                    patches = []
                    for patch in method['patches']:
                        extracted_patches = extract_fixed_method(patch) 
                        patches.append(extracted_patches)
                method['extracted_patches'] = patches

            with open("/Users/aslan/Desktop/MFRepair_ubuntu/resources/validation_data.json", "w") as file:
                json.dump(data, file, indent=4)
            print(bug_id)
    except Exception as error:
        print(error)
        with open("/Users/aslan/Desktop/MFRepair_ubuntu/resources/error_bugs.txt", "r") as file:
            text=file.read()
        with open("/Users/aslan/Desktop/MFRepair_ubuntu/resources/error_bugs.txt", "w") as file:
            file.write(f"{text}\n{bug_id}-{n}-{error}-{'no_relatable_failing_tests' in method}")
        print(f"{bug_id}-{n}-ERROR")  



if __name__ == '__main__':
    main() 
