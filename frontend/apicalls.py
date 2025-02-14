import re
import dask
from dask.distributed import Client
import requests
import time
# Hardcoded API key (⚠️ INSECURE - only for temporary/local use)
GROQ_API_KEY = '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'

def parse_transcript(transcript_text):
    entries = []
    parts = transcript_text.split('Timestamp: ')[1:]
    for part in parts:
        part = part.strip()
        if not part:
            continue
        time_end = part.find(' - Text: ')
        if time_end == -1:
            continue
        timestamp_str = part[:time_end]
        text = part[time_end+len(' - Text: '):]
        try:
            timestamp = float(timestamp_str.replace('s', '').strip())
        except ValueError:
            continue
        entries.append({'timestamp': timestamp, 'text': text.strip()})
    
    # Debugging: print the first few timestamps to check their range
    print(f"Parsed timestamps: {entries[:5]}")
    return entries

def split_into_chunks(entries, max_words=1800):
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for entry in entries:
        entry_words = len(entry['text'].split())
        if current_word_count + entry_words > max_words:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_word_count = 0
            if entry_words > max_words:
                chunks.append([entry])
                continue
        current_chunk.append(entry)
        current_word_count += entry_words
    
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def parse_chapters(response_text):
    chapters = []
    pattern = r'Start Time: ([\d.]+)s, End Time: ([\d.]+)s - Chapter Name: (.*)'
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            line = line[1:].strip()
            match = re.match(pattern, line)
            if match:
                chapters.append({
                    'start': float(match.group(1)),
                    'end': float(match.group(2)),
                    'name': match.group(3).strip()
                })
    return chapters

@dask.delayed
def process_chunk(chunk_entries):
    try:
        chunk_text = "\n".join(
            f"Timestamp: {entry['timestamp']}s - Text: {entry['text']}" 
            for entry in chunk_entries
        )
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "messages": [{
                    "role": "user",
                    "content": f"""Analyze this video transcript segment and generate chapter names with timestamps. 
                                make sure the timings match with the appropriate boundaries accoridng to given transcript Format:
                                - Start Time: [start]s, End Time: [end]s - Chapter Name: [name]
                                
                                Transcript:
                                {chunk_text}"""
                }],
                "model": "mixtral-8x7b-32768",
                "temperature": 0.7
            },
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            if response.status_code == 429:  # Rate limit exceeded
                wait_time = float(response.json()['error']['message'].split("in ")[1].split("s")[0])
                print(f"Rate limit exceeded. Waiting for {wait_time}s...")
                time.sleep(wait_time)  # Wait for the specified time
            return []
            
        content = response.json()['choices'][0]['message']['content']
        return parse_chapters(content)
    
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return []

def main():
    client = Client()
    
    with open('data.txt', 'r') as f:
        transcript = f.read()
    
    entries = parse_transcript(transcript)
    chunks = split_into_chunks(entries)
    
    futures = [process_chunk(chunk) for chunk in chunks]
    results = dask.compute(*futures)
    
    all_chapters = [chap for sublist in results for chap in sublist]
    all_chapters.sort(key=lambda x: x['start'])
    
    print("\nGenerated Chapters:")
    for chap in all_chapters:
        print(f"{chap['start']:.2f}s - {chap['end']:.2f}s: {chap['name']}")

if __name__ == "__main__":
    main()