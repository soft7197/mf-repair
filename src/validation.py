import lib
import json
import subprocess
from step_1_map_construction import replace_method_auto, run_tests, extract_failed_test_cases
from step_4_extracting_patches_from_output import get_method_name
import os


CHECKOUT_DIR = ""
WORK_DIR = ""

def main():
    with open (f"{WORK_DIR}/resources/validation_data.json", "r") as file:
        data=json.load(file)
    for bug_id in data:
        lib.checkout_project_buggy(bug_id.split('_')[0], bug_id.split('_')[1], f"{CHECKOUT_DIR}/{bug_id}")
        n=0
        for method in data[bug_id]['functions']:
            n+=1
            try:
                if 'patches' not in method:
                    continue
                if 'directly_related_tests' in method:
                    plausible=[]
                    for patch in method['extracted_patches']:
                        replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{method['path']}", patch [0], method['buggy_function'])
                        run_tests(f"{CHECKOUT_DIR}/{bug_id}")
                        replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{method['path']}", method['buggy_function'], method['buggy_function'])
                        if not os.path.exists(f"{CHECKOUT_DIR}/{bug_id}/failing_tests"):
                            continue
                        with open (f"{CHECKOUT_DIR}/{bug_id}/failing_tests") as file :
                            failing_tests=extract_failed_test_cases(file.read())
                        all_failing_tests = [test for test in data[bug_id]['trigger_test']]
                        if set(method['directly_related_tests']) == set([t for t in all_failing_tests if t not in failing_tests]):
                            plausible.append(patch[0])
                    method["plausible"]=plausible
                    print(f"{bug_id}-{n} checked")
                elif 'non_directly_related_tests' in method:
                    for patchset in method['extracted_patches']:
                        for patch in patchset:
                            patch_name = get_method_name(patch)
                            for mm in data[bug_id]['functions']:
                                if get_method_name(mm['buggy_function'] == patch_name) :
                                    replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{mm['path']}", patch, mm['buggy_function'])
                        run_tests(f"{CHECKOUT_DIR}/{bug_id}")
                        for mm in data[bug_id]['functions']:
                                if get_method_name(mm['buggy_function'] == patch_name) :
                                    replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{mm['path']}", mm['fixed_function'], mm['buggy_function'])
                        if not os.path.exists(f"{CHECKOUT_DIR}/{bug_id}/failing_tests"):
                            continue
                        with open (f"{CHECKOUT_DIR}/{bug_id}/failing_tests") as file :
                            failing_tests=extract_failed_test_cases(file.read())
                        all_failing_tests = [test for test in data[bug_id]['trigger_test']]
                        direct_tests=[]
                        for mm2 in data[bug_id]['functions']:
                            if 'directly_related_tests' in mm2:
                                direct_tests += mm2['directly_related_test']
                        if set(failing_tests) == set([t for t in all_failing_tests if t not in direct_tests]):
                            plausible.append(patch[0])
            except Exception as error:
                with open(f"{WORK_DIR}/resources/error_bugs.txt", "r") as file:
                    text=file.read()
                with open(f"{WORK_DIR}/resources/error_bugs.txt", "w") as file:
                    file.write(f"{text}\n{bug_id}-{n}-{error}")
                print(f"{bug_id}-{n}-ERROR")  
                
        with open(f"{WORK_DIR}/resources/validated_data.json", "w") as file:
            json.dump(data, file, indent=4)             


if __name__ == '__main__':
    main()
