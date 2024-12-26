import subprocess
import json

def checkout_project_buggy(project_id, bug_id, work_dir):
    """Checks out the project from Defects4J."""
    command = f"defects4j checkout -p {project_id} -v {bug_id}b -w {work_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error during checkout: {result.stderr}")
        return False
    print(f"Checked out project {project_id} (bug {bug_id}) to {work_dir}")
    return True

def checkout_project_fixed(project_id, bug_id, work_dir):
    """Checks out the project from Defects4J."""
    command = f"defects4j checkout -p {project_id} -v {bug_id}f -w {work_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error during checkout: {result.stderr}")
        return False
    print(f"Checked out project {project_id} (bug {bug_id}) to {work_dir}")
    return True

def main():
    with open("/home/selab/Desktop/MFRepair_ubuntu/resources/defects4jv1-mf.json","r") as file:
        data=json.load(file)
    bug_ids=[]    
    for key in data:
        bug_ids.append(key)
    
    for bug_id in bug_ids:
        if bug_id != 'Chart_22':
            continue
        checkout_project_buggy(bug_id.split('_')[0], bug_id.split('_')[1], f"/home/selab/Desktop/MFRepair_ubuntu/resources/checkout/{bug_id}") 
        #checkout_project_fixed(bug_id.split('-')[0], bug_id.split('-')[1], f"/Users/aslan/Desktop/defects4j_mf/{bug_id.split('-')[0]}_{bug_id.split('-')[1]}_fixed") 
        print(bug_id)

if __name__ == "__main__":
    main()
