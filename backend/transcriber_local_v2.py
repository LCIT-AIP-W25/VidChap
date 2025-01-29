# import subprocess
# import json
# from vosk import Model, KaldiRecognizer
# from pydub import AudioSegment
# import io

# # Path to the Vosk model directory (adjust the path to your model)
# model_path = "vosk-model-small-en-us-0.15"  # Replace with the actual path to your model folder

# # Path to the MP3 file (replace with your MP3 file path)
# mp3_file = "audio.mp3"  # Replace with your MP3 file path


# def convert_mp3_to_wav_with_ffmpeg(mp3_file):
#     # Use ffmpeg to convert MP3 to WAV in memory
#     command = [
#         "ffmpeg", "-i", mp3_file, "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", "-f", "wav", "pipe:1"
#     ]
#     result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     if result.returncode != 0:
#         raise Exception(f"Error during MP3 to WAV conversion: {result.stderr.decode()}")
    
#     # Return the WAV audio data and sample rate (16000)
#     return result.stdout, 16000


# # Use the function to convert MP3 to WAV data in memory
# audio_data, sample_rate = convert_mp3_to_wav_with_ffmpeg(mp3_file)

# # Load the Vosk Small English model
# model = Model(model_path)

# # Initialize the recognizer with the sample rate from the converted audio
# recognizer = KaldiRecognizer(model, sample_rate)

# # Function to convert chunk to audio data
# def chunk_to_audio_data(chunk):
#     with io.BytesIO() as buffer:
#         chunk.export(buffer, format="wav")
#         buffer.seek(0)
#         return buffer.read()

# # Chunk duration in milliseconds (10 seconds)
# chunk_duration = 10000  # 10 seconds in milliseconds

# # Initialize the AudioSegment object from the in-memory WAV
# audio = AudioSegment.from_wav(io.BytesIO(audio_data))

# # Process each 10-second chunk
# transcript = []
# for i in range(0, len(audio), chunk_duration):
#     chunk = audio[i:i + chunk_duration]
#     audio_data_chunk = chunk_to_audio_data(chunk)

#     # Feed the audio chunk to the recognizer
#     recognizer.AcceptWaveform(audio_data_chunk)
    
#     # Capture intermediate results
#     partial_result = recognizer.PartialResult()
#     result_dict = json.loads(partial_result)
    
#     # Add words with timestamps from PartialResult to the transcript
#     if "result" in result_dict:
#         for word_info in result_dict["result"]:
#             transcript.append({
#                 "start": word_info["start"],
#                 "end": word_info["end"],
#                 "word": word_info["word"]
#             })

# # Final result in case there's any remaining data
# final_result = recognizer.FinalResult()
# final_result_dict = json.loads(final_result)
# if "result" in final_result_dict:
#     for word_info in final_result_dict["result"]:
#         transcript.append({
#             "start": word_info["start"],
#             "end": word_info["end"],
#             "word": word_info["word"]
#         })
#         # print(transcript)


# # Print the transcript with timestamps
# print("Full Transcript with Timestamps:")
# for entry in transcript:
#     print(f"[{entry['start']:.2f}s - {entry['end']:.2f}s] {entry['word']}")
