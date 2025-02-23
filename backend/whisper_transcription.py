from faster_whisper import WhisperModel

model_size = "large-v3"

# Run on CPU instead of GPU
model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe("C:\Marmik\VidChap\backend\audio.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))



segments, _ = model.transcribe("C:\Marmik\VidChap\backend\audio.mp3")
segments = list(segments)  # The transcription will actually run here.



#------------------------- New Features to be added ----------------# 

#Batched Transcription

# from faster_whisper import WhisperModel, BatchedInferencePipeline

# model = WhisperModel("turbo", device="cuda", compute_type="float16")
# batched_model = BatchedInferencePipeline(model=model)
# segments, info = batched_model.transcribe("audio.mp3", batch_size=16)

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))


#Faster Distil-Whisper

# from faster_whisper import WhisperModel

# model_size = "distil-large-v3"

# model = WhisperModel(model_size, device="cuda", compute_type="float16")
# segments, info = model.transcribe("audio.mp3", beam_size=5, language="en", condition_on_previous_text=False)

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

#Word-level timestamps

# segments, _ = model.transcribe("audio.mp3", word_timestamps=True)

# for segment in segments:
#     for word in segment.words:
#         print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
