import cv2
import numpy as np
import datetime
import pyaudio
import wave

#時間取得
now = datetime.datetime.now()

rec_time = 3  # 録音時間[s]


##音声
file_path = str(now)+".wav"  # 音声を保存するファイル名
audio_fmt = pyaudio.paInt16  # 音声のフォーマット
ch = 1  # チャンネル1(モノラル)
sampling_rate = 11025  # サンプリング周波数
chunk = 1024  # チャンク（データ点数）
audio = pyaudio.PyAudio()
audio_stream = audio.open(format=audio_fmt, channels=ch, rate=sampling_rate, input=True,
                    frames_per_buffer=chunk)
frames = []

##動画
cap = cv2.VideoCapture(0)
fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
fps = 40.0
size = (640, 360)
writer = cv2.VideoWriter(str(now)+'.mov', fmt, fps, size)
cnt = 0

# # 録音処理
# frames = []
# for i in range(0, int(sampling_rate / chunk * rec_time)):
#     data = audio_stream.read(chunk)
#     frames.append(data)
#
# print("recording  end...")
#
# # 録音終了処理
# audio_stream.stop_stream()
# audio_stream.close()
# audio.terminate()
#
# # 録音データをファイルに保存
# wav = wave.open(file_path, 'wb')
# wav.setnchannels(ch)
# wav.setsampwidth(audio.get_sample_size(audio_fmt))
# wav.setframerate(sampling_rate)
# wav.writeframes(b''.join(frames))
# wav.close()
while 1:
    # try:
    #     data = audio_stream.read(chunk)
    #     frames.append(data)
    #     print(data)
    # except OSError as ex:
    #     print(ex)
    if cap.isOpened():
        # 音声

        # 動画
        _, frame = cap.read()
        frame = cv2.resize(frame, size)
        writer.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 13:
            writer.release()
            now = datetime.datetime.now()
            writer = cv2.VideoWriter(str(now) + '.mov', fmt, fps, size)
        elif cv2.waitKey(1) == 113:
            break

        cnt += 1
        sec = int(cnt / fps)
        if(sec == rec_time):
            print(cnt)
            now = datetime.datetime.now()
            # #音声
            # # 録音終了処理
            # audio_stream.stop_stream()
            # audio_stream.close()
            # audio.terminate()
            # # 録音データをファイルに保存
            # wav = wave.open(file_path, 'wb')
            # wav.setnchannels(ch)
            # wav.setsampwidth(audio.get_sample_size(audio_fmt))
            # wav.setframerate(sampling_rate)
            # wav.writeframes(b''.join(frames))
            # wav.close()
            #
            # #新たに音声ファイルを作成
            # file_path = str(now) + ".wav"  # 音声を保存するファイル名
            # wav = wave.open(file_path, 'wb')
            # wav.setnchannels(ch)
            # wav.setsampwidth(audio.get_sample_size(audio_fmt))
            # wav.setframerate(sampling_rate)

            #新たに動画ファイルを作成
            cnt = 0
            writer.release()
            writer = cv2.VideoWriter(str(now) + '.mov', fmt, fps, size)

# # 録音終了処理
# audio_stream.stop_stream()
# audio_stream.close()
# audio.terminate()
# wav.close()

# 動画終了処理
writer.release()
cap.release()
cv2.destroyAllWindows()