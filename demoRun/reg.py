import re

def extract_chapter_data(text):
    pattern = r"\[chapter : (.*?) (\d+\.\d+)s (\d+\.\d+)s\]"
    
    chapter_names = []
    start_times = []
    end_times = []
    
    matches = re.findall(pattern, text)
    
    for match in matches:
        chapter_names.append(match[0])
        start_times.append(float(match[1]))
        end_times.append(float(match[2]))
    
    return chapter_names, start_times, end_times

# Example usage
data = """[chapter : Introduction to the Cable Tester 0.00s 20.00s]
[chapter : First Impressions and Description 20.00s 50.00s]
[chapter : Testing the Cable Tester 50.00s 80.00s]
[chapter : Testing Various Cables 80.00s 150.00s]
[chapter : Testing USB and Other Cables 150.00s 220.00s]
[chapter : Real-World Use Cases and Examples 220.00s 320.00s]
[chapter : Testing Audio Cables and Adapters 320.00s 410.00s]
[chapter : Examining Different Types of Cables 410.00s 480.00s]
[chapter : Conclusion and Final Thoughts 480.00s 529.68s]"""

chapters, starts, ends = extract_chapter_data(data)

print("Chapters:", chapters)
print("Start Times:", starts)
print("End Times:", ends)
