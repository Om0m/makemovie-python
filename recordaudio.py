# -*- coding: utf-8 -*
import pyaudio
import wave

rec_time = 3  # 録音時間[s]
file_path = "a.wav"  # 音声を保存するファイル名
fmt = pyaudio.paInt16  # 音声のフォーマット
ch = 1  # チャンネル1(モノラル)
sampling_rate = 14000  # サンプリング周波数
chunk = 1024  # チャンク（データ点数）
audio = pyaudio.PyAudio()

stream = audio.open(format=fmt, channels=ch, rate=sampling_rate, input=True,
                    frames_per_buffer=chunk)
print("recording start...")

# 録音処理
frames = []
for i in range(0, int(sampling_rate / chunk * rec_time)):
    print(i) #31回実行した
    data = stream.read(chunk)
    print(data,len(data))
    frames.append(data)

print("recording  end...")

# 録音終了処理
stream.stop_stream()
stream.close()
audio.terminate()

# 録音データをファイルに保存
wav = wave.open(file_path, 'wb')
wav.setnchannels(ch)
wav.setsampwidth(audio.get_sample_size(fmt))
wav.setframerate(sampling_rate)
wav.writeframes(b''.join(frames))
wav.close()
