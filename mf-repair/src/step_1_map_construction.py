import lib

import subprocess
import json
import re
import shutil
import javalang
import os   


def run_tests(work_dir):
    command = f"defects4j test -w {work_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stderr

def checkout_project(project_id, bug_id, work_dir):
    """Checks out the project from Defects4J."""
    command = f"defects4j checkout -p {project_id} -v {bug_id}f -w {work_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error during checkout: {result.stderr}")
        return False
    print(f"Checked out project {project_id} (bug {bug_id}) to {work_dir}")
    return True


def copy_java_file(source_path, destination_path):
    try:
        shutil.copy(source_path, destination_path)
        print(f"File copied successfully from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"Source file not found: {source_path}")
    except PermissionError:
        print(f"Permission denied while copying to: {destination_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def replace_method_auto(java_file_path, fixed_method_code, buggy_method_code):
    # Step 1: Read the Java file
    with open(java_file_path, 'r') as file:
        java_code = file.read()

    # Step 2: Parse the fixed method signature
    if fixed_method_code is not None:
        method_signature_match = re.search(r'(?:(public|protected|private)\s+)?(?:static\s+)?(?:[\w<>]+\s+)?(\w+)\s*\((.*?)\)\s*\{', fixed_method_code, re.DOTALL)
        if not method_signature_match:
            print("Invalid fixed method code. Ensure it contains a valid method signature.")
            return
    else:
        fixed_method_code=""
        method_signature_match = re.search(r'(?:(public|protected|private)\s+)?(?:static\s+)?(?:[\w<>]+\s+)?(\w+)\s*\((.*?)\)\s*\{', buggy_method_code, re.DOTALL)
        if not method_signature_match:
            print("Invalid fixed method code. Ensure it contains a valid method signature.")
            return
    fixed_method_name = method_signature_match.group(2)
    #fixed_param_types = [param.strip().split()[0].replace('[', '').replace(']','') for param in method_signature_match.group(3).split(',') if param.strip()]
    fixed_param_types = [
        re.sub(r'@Nullable\s*|final\s*', '', param.strip()).split()[0]  # Remove @Nullable and final
        .replace('[', '').replace(']', '')  # Remove array brackets
        .split('<')[0]  # Extract type before the generic
        for param in method_signature_match.group(3).split(',') 
        if param.strip()
    ]
    # Step 3: Parse the Java code to locate the buggy method
    tree = javalang.parse.parse(java_code)
    java_lines = java_code.splitlines()

    buggy_method_start = None
    buggy_method_end = None

    for path, node in tree:
        if (isinstance(node, javalang.tree.MethodDeclaration) or isinstance(node, javalang.tree.ConstructorDeclaration)) and node.name == fixed_method_name:
            # Extract parameter types for comparison
            node_param_types = [param.type.name for param in node.parameters]
            if node_param_types == fixed_param_types:
                # Found the matching method
                buggy_method_start = node.position.line - 1  # Convert to 0-based index
                current_line = buggy_method_start
                bracket_balance = 0
                found_opening = False

                # Traverse lines to find the closing bracket of the method
                while current_line < len(java_lines):
                    line = java_lines[current_line]
                    # Count opening and closing brackets
                    bracket_balance += line.count('{')
                    bracket_balance -= line.count('}')

                    if '{' in line:
                        found_opening = True
                    if found_opening and bracket_balance == 0:
                        buggy_method_end = current_line
                        break

                    current_line += 1
                break

    if buggy_method_start is None or buggy_method_end is None:
        print(f"Method {fixed_method_name} with parameters {fixed_param_types} not found in the file.")
        return


    # Step 5: Replace the method
    updated_lines = (
        java_lines[:buggy_method_start]
        + fixed_method_code.splitlines()
        + java_lines[buggy_method_end+1:]
    )

    # Step 6: Write the updated code back to the file
    with open(java_file_path, 'w') as file:
        file.write("\n".join(updated_lines))
    
    print(f"Method {fixed_method_name} successfully replaced!")

def extract_failed_test_cases(log):
    failure_pattern = re.compile(r"--- ([\w\.]+)::([\w\d_]+)")
    failed_tests = failure_pattern.findall(log)
    failed_test_cases = [f"{suite}::{test}" for suite, test in failed_tests]
    
    return failed_test_cases


def main():

    checked_out_projects_path="/Users/selab/Desktop/MFRepair/resources/checkedouts"

    with open("/Users/selab/Desktop/MFRepair/resources/defects4j-mf_copy.json","r") as file:
        data=json.load(file)
    with open("/Users/selab/Desktop/MFRepair/resources/defects4jv1-mf.json","r") as file:
        processed_bugs=json.load(file)    
    bug_ids=[]   
    for key in data:
        bug_ids.append(key)
    for bug_id in bug_ids:
        bug_id=bug_id.replace('-','_')
        if bug_id in ['Math_49']:  #.split('_')[0] in ['Chart','Closure','Math','Time','Lang','Mockito'] and bug_id not in processed_bugs.keys():
            try:
                lib.checkout_project_buggy(bug_id.split('_')[0], bug_id.split('_')[1], f"{checked_out_projects_path}/{bug_id}")
                run_tests(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}")
                with open(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}/failing_tests",'r') as file:
                        log=file.read() 
                all_failing_tests = extract_failed_test_cases(log)
                directly_related_tcs_list=[]
                for method in data[bug_id.replace('_','-')]['functions']:
                    replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['fixed_function'], method['buggy_function'])
                    run_tests(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}")
                    if os.path.exists(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}/failing_tests"):
                        with open(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}/failing_tests",'r') as file:
                            log=file.read()
                    else:
                        method['Compiling error!']=True
                        method['non_directly_related_tests']=[]
                        replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['fixed_function'], method['buggy_function'])
                        continue
                    current_failed_test_cases = extract_failed_test_cases(log)
                    related_test_cases = [item for item in all_failing_tests if item not in current_failed_test_cases]
                    if len(related_test_cases)>0:
                        method['directly_related_tests'] = related_test_cases
                        directly_related_tcs_list+=related_test_cases
                    else:
                        method['non_directly_related_tests']=[]
                    replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['buggy_function'], method['buggy_function'])
                left_test_cases = [item for item in all_failing_tests if item not in directly_related_tcs_list]
                for method in data[bug_id.replace('_','-')]['functions']:
                    if 'non_directly_related_tests' in method:
                        replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['fixed_function'], method['buggy_function'])
                run_tests(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}")
                with open(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}/failing_tests",'r') as file:
                        log=file.read() 
                current_failed_test_cases = extract_failed_test_cases(log) 
                if set(current_failed_test_cases) == set(directly_related_tcs_list): 
                    for method in data[bug_id.replace('_','-')]['functions']:
                        if 'non_directly_related_tests' in method:
                            replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['buggy_function'], method['buggy_function'])
                            run_tests(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}")
                            with open(f"{checked_out_projects_path}/{bug_id.split('_')[0]}_{bug_id.split('_')[1]}/failing_tests",'r') as file:
                                log=file.read()
                            if set(extract_failed_test_cases(log)) == set(current_failed_test_cases):
                                method['no_relatable_failing_tests']=True
                            replace_method_auto(f"{checked_out_projects_path}/{bug_id}/{method['path']}", method['fixed_function'], method['buggy_function'])
                    for method in data[bug_id.replace('_','-')]['functions']:
                        if 'non_directly_related_tests' in method and 'no_relatable_failing_tests' not in method:
                            method['non_directly_related_tests']=left_test_cases
                else:
                    left_relatable_tests = [item for item in left_test_cases if item not in current_failed_test_cases]
                    if len(left_relatable_tests)>0:
                        for method in data[bug_id.replace('_','-')]['functions']:
                            if 'non_directly_related_tests' in method:
                                method['non_directly_related_tests']=left_relatable_tests
                    else:
                        for method in data[bug_id.replace('_','-')]['functions']:
                            if 'non_directly_related_tests' in method:
                                method['non_directly_related_tests']=[item for item in all_failing_tests if item not in current_failed_test_cases]
                processed_bugs[bug_id]=data[bug_id.replace('_','-')]                       
                with open("/Users/selab/Desktop/MFRepair/resources/defects4jv1-mf.json", "w") as file:
                    json.dump(processed_bugs, file, indent=4)
            except Exception as a:
                print(a)

if __name__ == "__main__":
    main()
