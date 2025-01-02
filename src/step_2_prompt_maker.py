from importlib.resources import Package
import json
import lib


checked_out_projects_path = ""
WORK_DIR=""

def get_failed_line(file_path, line_number):
    if line_number < 1:
        raise ValueError("Line number must be greater than or equal to 1.")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for current_line_number, line in enumerate(file, start=1):
                if current_line_number == line_number:
                    return line.rstrip()  # Remove newline or extra whitespace
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at '{file_path}' does not exist.")

    raise IndexError(f"Line {line_number} is out of range for file '{file_path}'.")



def generate_llm_prompt(bug_id, bug_json, working_dir):

    direct_methods = [item for item in bug_json['functions'] if 'directly_related_tests' in item]
    non_direct_methods = [item for item in bug_json['functions'] if 'non_directly_related_tests' in item and 'no_relatable_failing_tests' not in item]
    methods_without_testcase = [item for item in bug_json['functions'] if 'no_relatable_failing_tests' in item] 
    
    # --- making promt for directly connected method&test case pairs 

    for method in direct_methods:
        #Head-promt 
        prompt = "### **Task**\n"
        prompt += "You are given a buggy function. Your goal is to fix the function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"
        
        prompt += "\n### **Buggy Function**\n"
        prompt += "Here is the source code of the **buggy function** that requires fixing. Please review the logic carefully.\n\n"
        prompt += "```java\n"
        prompt += method['buggy_function'].strip()
        prompt += "\n```\n\n"
        prompt += "### **Function Comment**\n"
        prompt += "Below is the official comment for the function. It provides additional context on the function's purpose and intended logic.\n\n"
        prompt += "```\n"
        prompt += method['comment'].strip()
        prompt += "\n```\n\n"
        
        prompt += "### **Failing Test Case(s)**\n"
        prompt += "The following test case(s) failed due to issues in the function. The details include the test code, the line where the failure occurred, and the associated error message. Use this information to identify the source of the bug.\n\n"
        
        count = 1
        for test_case_key in method['directly_related_tests']:
            prompt += f"#### **Test {count}:**\n"
            if 'failed_line' in bug_json['trigger_test'][test_case_key]:
                file_path = f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}"
                failed_line = get_failed_line(file_path, bug_json['trigger_test'][test_case_key]['failed_line'])
                prompt += f"**Failed Line:** `{failed_line}`\n\n"
                #prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
            prompt += "**Test Code:**\n"
            prompt += "```java\n"
            prompt += bug_json['trigger_test'][test_case_key]['src'].strip()
            prompt += "\n```\n\n"
            prompt += "**Error Message:**\n"
            prompt += "```\n"
            prompt += bug_json['trigger_test'][test_case_key]['clean_error_message'].strip()
            prompt += "\n```\n\n"
            count+=1

        prompt += "**Return the fixed function with inline comments.**"
        method['llm_promt'] = prompt

    # making promt for not-directly connected method&test case pairs 

    for method in non_direct_methods:
        #Head-promt 
        prompt = "### **Task**\n"
        prompt += "You are given several buggy functions. Your goal is to fix each function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"
        count = 0 
        for method in non_direct_methods:
            prompt += f"### **Buggy Function {count}:**\n"
            prompt += "```java\n"
            prompt += method['buggy_function'].strip()
            prompt += "\n```\n\n"
            prompt += "### **Function Comment**\n"
            prompt += "Below is the official comment for the function. It provides additional context on the function's purpose and intended logic.\n\n"
            prompt += "```\n"
            prompt += method['comment'].strip()
            prompt += "\n```\n\n"
            count+=1
            
        prompt += "### **Failing Test Case(s)**\n"
        prompt += "The following test case(s) failed due to issues in the functions(s). The details include the test code(s), the line where the failure occurred, and the associated error message. Use this information to identify the source of the bug.\n\n"
        
        count=0
        for test_case_key in method['non_directly_related_tests']:
            prompt += f"#### **Test {count}: **\n"
            if 'failed_line' in bug_json['trigger_test'][test_case_key]:
                file_path = f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}"
                failed_line = get_failed_line(file_path, bug_json['trigger_test'][test_case_key]['failed_line'])
                prompt += f"**Failed Line:** `{failed_line}`\n\n"
                #prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
            prompt += "**Test Code:**\n"
            prompt += "```java\n"
            prompt += bug_json['trigger_test'][test_case_key]['src'].strip()
            prompt += "\n```\n\n"
            prompt += "**Error Message:**\n"
            prompt += "```\n"
            prompt += bug_json['trigger_test'][test_case_key]['clean_error_message'].strip()
            prompt += "\n```\n\n"
            count+=1

        prompt += "**Return the fixed function(s) with inline comments.**"
        method['llm_promt'] = prompt
        
    #--- making promt to check without mapping and combination 
    
    #Head-promt 
    prompt = "### **Task**\n"
    prompt += "You are given several buggy functions. Your goal is to fix each function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"
    count = 0 
    for method in bug_json['functions']:
        prompt += f"### **Buggy Function {count}:**\n"
        prompt += "```java\n"
        prompt += method['buggy_function'].strip()
        prompt += "\n```\n\n"
        prompt += "### **Function Comment**\n"
        prompt += "Below is the official comment for the function. It provides additional context on the function's purpose and intended logic.\n\n"
        prompt += "```\n"
        prompt += method['comment'].strip()
        prompt += "\n```\n\n"
        count+=1
        
    prompt += "### **Failing Test Case(s)**\n"
    prompt += "The following test case(s) failed due to issues in the functions(s). The details include the test code(s), the line where the failure occurred, and the associated error message. Use this information to identify the source of the bug.\n\n"
    
    count=0
    for test_case_key in bug_json['trigger_test']:
        prompt += f"#### **Test {count}: **\n"
        if 'failed_line' in bug_json['trigger_test'][test_case_key]:
            file_path = f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}"
            failed_line = get_failed_line(file_path, bug_json['trigger_test'][test_case_key]['failed_line'])
            #prompt += f"**Failed Line:** `{failed_line}`\n\n"
            #prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
        prompt += "**Test Code:**\n"
        prompt += "```java\n"
        prompt += bug_json['trigger_test'][test_case_key]['src'].strip()
        prompt += "\n```\n\n"
        prompt += "**Error Message:**\n"
        prompt += "```\n"
        prompt += bug_json['trigger_test'][test_case_key]['clean_error_message'].strip()
        prompt += "\n```\n\n"
        count+=1

    prompt += "**Return the fixed function(s) with inline comments.**"
    bug_json['llm_promt_without_mapping'] = prompt

def prompt_remaking(patch, failing_tests, bug_json, working_dir, bug_id):      
    prompt = "### **Task**\n"
    prompt += "You are given several buggy functions. Your goal is to fix each function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"

    prompt += "\n###**Buggy Function**\n"
    prompt += "```java\n"
    prompt += patch.strip()
    prompt += "\n```\n\n"

    prompt += "### **Failing Test Case(s)**\n"
    prompt += "The following test case(s) failed due to issues in the function. Use this information to identify the source of the bug.\n\n"
    
    count = 1
    for test_case_key in failing_tests:
        prompt += f"#### **Test {count}:**\n"
        if 'failed_line' in bug_json['trigger_test'][test_case_key]:
            file_path = f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}"
            failed_line = get_failed_line(file_path, bug_json['trigger_test'][test_case_key]['failed_line'])
            prompt += f"**Failed Line:** `{failed_line}`\n\n"
            #prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
        prompt += "**Test Code:**\n"
        prompt += "```java\n"
        prompt += bug_json['trigger_test'][test_case_key]['src'].strip()
        prompt += "\n```\n\n"
        prompt += "**Error Message:**\n"
        prompt += "```\n"
        prompt += bug_json['trigger_test'][test_case_key]['clean_error_message'].strip()
        prompt += "\n```\n\n"
        count+=1
    prompt += "**Return the fixed function with inline comments.**"
    return prompt

def few_shot_prompt(buggy_method, fixed_function, method_json):      
    prompt+= "A reference pair of a buggy function and its corresponding fixed version is provided."
    prompt += "The goal is to use the insights from this fixed version to adjust or repair a new buggy function."
    prompt += "\n###**Reference Buggy Function**\n"
    prompt += "```java\n"
    prompt += buggy_method.strip()
    prompt += "\n```\n\n"
    prompt += "\n###**Its Fixed Version**\n"
    prompt += "```java\n"
    prompt += fixed_function.strip()
    prompt += "\n```\n\n"
    prompt += "**Buggy method to be fixed**\n"
    prompt += "```java\n"
    prompt += method_json['buggy_function'].strip()
    prompt += "\n```\n\n"
    return prompt


def main():

    with open(f"{WORK_DIR}/resources/defects4j-mf.json", "r") as file:
        data = json.load(file)
    for bug in data:
        lib.checkout_project_buggy(bug.split('_')[0], bug.split('_')[1], f"{checked_out_projects_path}/{bug}")
        generate_llm_prompt (bug, data[bug], checked_out_projects_path)
        print(bug)  
    with open(f"{WORK_DIR}/resources/validation_data.json", "w") as file:
        json.dump(data, file, indent=4)  



if __name__ == "__main__":
    main()