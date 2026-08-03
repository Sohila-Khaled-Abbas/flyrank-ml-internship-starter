import json
import os
import io
import sys
import contextlib

def run_notebook(notebook_path):
    print(f"Executing notebook top-to-bottom: {notebook_path}")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Execution context dictionary
    exec_globals = {}
    
    # Change directory to notebook directory during execution so relative paths match
    nb_dir = os.path.dirname(os.path.abspath(notebook_path))
    original_cwd = os.getcwd()
    
    try:
        os.chdir(nb_dir)
        exec_count = 1
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                source_code = ''.join(cell.get('source', []))
                stdout_capture = io.StringIO()
                
                print(f"Running cell {exec_count}...")
                cell['execution_count'] = exec_count
                
                with contextlib.redirect_stdout(stdout_capture):
                    try:
                        exec(source_code, exec_globals)
                        output_text = stdout_capture.getvalue()
                        cell['outputs'] = [
                            {
                                "name": "stdout",
                                "output_type": "stream",
                                "text": output_text.splitlines(keepends=True)
                            }
                        ]
                    except Exception as e:
                        err_msg = f"Execution Error: {e}\n"
                        print(err_msg, file=sys.stderr)
                        cell['outputs'] = [
                            {
                                "name": "stderr",
                                "output_type": "stream",
                                "text": [err_msg]
                            }
                        ]
                        raise e
                exec_count += 1
    finally:
        os.chdir(original_cwd)
        
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print(f"Successfully executed and saved: {notebook_path}")

if __name__ == "__main__":
    run_notebook("work/notebooks/w01_research_question.ipynb")
    run_notebook("work/notebooks/w02_ml_task_framing.ipynb")
    run_notebook("work/notebooks/w03_data_contract.ipynb")
    run_notebook("work/notebooks/w04_baseline_score.ipynb")
    run_notebook("work/notebooks/capstone.ipynb")
