
from lib import predictor_CodeLlama
from lib import predictor_gpt_turbo
import os
import json 

BEAM_SIZE=10

def main():

    with open ("/home/selab/Desktop/MFRepair/resources/defects4jv1_mf_with_gptspatch.json", "r") as file:
        data=json.load(file)
    
    # for bug_id in data:
    #     n = 0
    #     if bug_id=='Time_3':
    #         for method in data[bug_id]['functions']:
    #             n += 1
    #             try:
    #                 method['patches'] = predictor_CodeLlama.generate_70b(method['llm_promt'])
    #                 with open("/home/selab/Desktop/MFRepair/resources/defects4jv1_mf_with_llamaspatch.json", "w") as file:
    #                     json.dump(data, file, indent=4)
    #             except Exception as error:
    #                 with open("/home/selab/Desktop/MFRepair/resources/error_bugs.txt", "w") as file:
    #                     file.writelines(f"{bug_id} method_num = {n} {error}")

    for bug_id in data:
        n = 0
        if bug_id != 'Math_6':
            continue

        for method in data[bug_id]['functions']:
            n += 1
            try:
                # patches = predictor_gpt_turbo.get_response(method['llm_promt'], BEAM_SIZE)
                # print(f"\n{bug_id}-{n}--------------------------------------------------------------------------------------------------\n")
                # for patch in patches:
                #     print(patch)

                method['patches'] = predictor_gpt_turbo.get_response(method['llm_promt'], BEAM_SIZE)
                with open("/home/selab/Desktop/MFRepair/resources/defects4jv1_mf_with_gptspatch.json", "w") as file:
                    json.dump(data, file, indent=4)
                print(f"{bug_id}-{n}-patch succesfully generated")
            except Exception as error:
                with open("/home/selab/Desktop/MFRepair/resources/error_bugs.txt", "r") as file:
                    text=file.read()
                with open("/home/selab/Desktop/MFRepair/resources/error_bugs.txt", "w") as file:
                    file.write(f"{text}\n{bug_id}-{n}-{error}-{'no_relatable_failing_tests' in method}")
                print(f"{bug_id}-{n}-ERROR")  

if __name__ == '__main__':
    main()    