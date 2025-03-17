from tabulate import tabulate
import subprocess
import json

def run_tests():
    # Run pytest and capture output
    result = subprocess.run(['pytest', '--json-report', '--json-report-file=report.json'], capture_output=True, text=True)
    
    # Load the JSON report
    with open('report.json') as f:
        report = json.load(f)
    
    # Prepare data for the dashboard
    test_results = []
    for test in report['tests']:
        test_results.append([test['nodeid'], test['outcome'], test['duration']])
    
    # Display the dashboard
    print(tabulate(test_results, headers=["Test Case", "Outcome", "Duration (s)"], tablefmt="grid"))

if __name__ == "__main__":
    run_tests()