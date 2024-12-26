import json

checked_out_projects_path="/Users/selab/Desktop/MFRepair/resources/checkedouts"

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
   
    #--- making promt for directly connected method&test case pairs 
    for method in direct_methods:
        #Head-promt 
        prompt = "### **Task**\n"
        prompt += "You are given a buggy function. Your goal is to fix the function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"
        prompt += "**Requirements:**\n"
        prompt += "1. Identify and fix the root cause of the problem in the buggy function.\n"
        prompt += "2. Ensure the function works correctly for all inputs, including edge cases.\n"
        prompt += "3. Make sure the related test case(s) pass without any errors or exceptions.\n"
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
                prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
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

    #--- making promt for not-directly connected method&test case pairs 

    for method in non_direct_methods:
        #Head-promt 
        prompt = "### **Task**\n"
        prompt += "You are given several buggy functions. Your goal is to fix each function, resolve the issues indicated by the test case failures, and eliminate any runtime exceptions.\n\n"
        prompt += "**Requirements:**\n"
        prompt += "1. Identify and fix the root cause of the problem in each buggy function.\n"
        prompt += "2. Ensure each function works correctly for all inputs, including edge cases.\n"
        prompt += "3. Make sure the related test case(s) pass without any errors or exceptions.\n\n"
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
                prompt += f"**Failed Line:** `{get_failed_line(f"{working_dir}/{bug_id}/{bug_json['trigger_test'][test_case_key]['path']}",bug_json['trigger_test'][test_case_key]['failed_line'])}`\n\n"
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

def main():
    with open("/Users/selab/Desktop/MFRepair/resources/defects4jv1-mf.json", "r") as file:
        data = json.load(file)
    for bug in data:
        generate_llm_prompt (bug, data[bug], checked_out_projects_path)
        print(bug)  
    with open("/Users/selab/Desktop/MFRepair/resources/defects4jv1_mf_with_promt.json", "w") as file:
        json.dump(data, file, indent=4)  



if __name__ == "__main__":
    main()