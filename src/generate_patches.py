
from step_1_map_construction import replace_method_auto, run_tests, extract_failed_test_cases
from step_4_extracting_patches_from_output import get_method_name, extract_fixed_method
from lib import predictor_gpt_turbo
from step_2_prompt_maker import prompt_remaking
import os

import json 

BEAM_SIZE=10
WORK_DIR=""
CHECKOUT_DIR=""

def main():
    with open (f"{WORK_DIR}/resources/validation_data.json", "r") as file:
        data=json.load(file)
    for bug_id in data:
        try: 
            for method in data[bug_id]['functions']:
                patches = predictor_gpt_turbo.get_response(method['llm_promt'], BEAM_SIZE)  
                if 'directly_related_tests' in method:
                    extr_patches = []
                    plausible = []
                    patch_fn=[]
                    for patch in patches:
                        extracted_patches = extract_fixed_method(patch) 
                        extr_patches.append(extracted_patches)
                    for patch in extr_patches:
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
                        elif len(failing_tests) < len(all_failing_tests):
                            patch_fn.append([patch, len(failing_tests), failing_tests])
                    if len(plausible)==0:
                        for patch in sorted(patch_fn, key=lambda x: x[1]):
                            new_patches=predictor_gpt_turbo.get_response(prompt_remaking(patch[0], patch[2], data[bug_id], WORK_DIR, bug_id), BEAM_SIZE)
                            extr_patches2 = []
                            for patch1 in new_patches:
                                extracted_patches2 = extract_fixed_method(patch1) 
                                extr_patches2.append(extracted_patches2)
                            for patch1 in extr_patches2:
                                replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{method['path']}", patch1 [0], method['buggy_function'])
                                run_tests(f"{CHECKOUT_DIR}/{bug_id}")
                                replace_method_auto(f"{CHECKOUT_DIR}/{bug_id}/{method['path']}", method['buggy_function'], method['buggy_function'])
                                if not os.path.exists(f"{CHECKOUT_DIR}/{bug_id}/failing_tests"):
                                    continue
                                with open (f"{CHECKOUT_DIR}/{bug_id}/failing_tests") as file :
                                    failing_tests1=extract_failed_test_cases(file.read())
                                all_failing_tests = [test for test in data[bug_id]['trigger_test']]                            
                                if set(method['directly_related_tests']) == set([t for t in all_failing_tests if t not in failing_tests1]):
                                    plausible.append(patch[0]) 
                                elif len(failing_tests1) < len(all_failing_tests):
                                    patch_fn.append([patch, len(failing_tests), failing_tests])
                    method['plausible'] = plausible   
                elif 'non_directly_related_tests' in method:
                    extr_patches = []
                    plausible = []
                    patch_fn=[]
                    for patch in patches:
                        extracted_patches = extract_fixed_method(patch) 
                        extr_patches.append(extracted_patches)
                    for patchset in extr_patches:
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
                        elif len(failing_tests) < len(all_failing_tests):
                            patch_fn.append([patch, len(failing_tests), failing_tests])
                        if len(plausible)==0:
                           for patch in sorted(patch_fn, key=lambda x: x[1]):
                                new_patches=predictor_gpt_turbo.get_response(prompt_remaking(patch[0], patch[2], data[bug_id], WORK_DIR, bug_id), BEAM_SIZE)
                                extr_patches = []
                                patch_fn=[]
                                for patch in patches:
                                    extracted_patches = extract_fixed_method(patch) 
                                    extr_patches.append(extracted_patches)
                                for patchset in extr_patches:
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
                    method['plausible'] = plausible 
                with open(f"{WORK_DIR}/resources/validation_data.json", "w") as file:
                    json.dump(data, file, indent=4)
        except Exception as error:
            with open(f"{WORK_DIR}/resources/error_bugs.txt", "r") as file:
                text=file.read()
            with open(f"{WORK_DIR}/resources/error_bugs.txt", "w") as file:
                file.write(f"{text}\n{bug_id}-{error}")
            print(f"{bug_id}-ERROR")  

if __name__ == '__main__':
    main()    
