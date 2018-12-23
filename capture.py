import cv2
import numpy as np
import datetime
import pyaudio
import wave
import time
# 時間取得
now = datetime.datetime.now()

rec_time = 10  # 録音時間[s]


class AudioFilter():
    def __init__(self):
        # オーディオに関する設定
        self.p = pyaudio.PyAudio()
        self.channels = 2  # マイクがモノラルの場合は1にしないといけない
        self.rate = 24000  # DVDレベルなので重かったら16000にする
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=False,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.callback)

    # コールバック関数（再生が必要なときに呼び出される）
    def callback(self, in_data, frame_count, time_info, status):
        out_data = in_data
        # data = self.stream.read(self.chunk)
        # print(out_data)
        frames.append(out_data)
        return (out_data, pyaudio.paContinue)

    def close(self):
        self.p.terminate()


frames = []

if __name__ == "__main__":
    # AudioFilterのインスタンスを作る場所
    af = AudioFilter()
    # ストリーミングを始める場所
    af.stream.start_stream()

    ##動画
    #0-4でソースが変わる
    cap = cv2.VideoCapture(3)
    print(cap)
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    #ソース元のfpsに合わせる必要あり
    fps = 30.0
    #size = (1920, 960)
    size = (640,360)
    writer = cv2.VideoWriter(str(now) + '.mov', fmt, fps, size)
    cnt = 0
    file_path = str(now) + ".wav"  # 音声を保存するファイル名

    start = time.time()
    while 1:
        if cap.isOpened():
            # 音声

            # 動画
            #start = time.time()

            _, frame = cap.read()
            frame = cv2.resize(frame, size)
            writer.write(frame)

            #end = time.time()
            now_time = time.time() - start
            if(now_time > 1.0):
                print(now_time,cnt)
                start = time.time()
            #print(end-start)

            #imshowをしたあとはwaitKeyなどで少しでも待たないと描画できない
            #cv2.imshow('frame', frame)
            if cv2.waitKey(1) == 113:
                break

            if cnt == 0:
                frames = []

            cnt += 1
            sec = int(cnt / fps)
            #print(cnt,"sec=",sec)
            #sec = int(now_time)
            if (sec == rec_time):
                elapsed_time = time.time() - start
                print(cnt,elapsed_time)
                # 時間取得
                now = datetime.datetime.now()
                # 音声
                # ストリーミングを止める場所
                af.stream.stop_stream()
                af.stream.close()
                af.close()
                # 音声
                # 録音データをファイルに保存
                wav = wave.open(file_path, 'wb')
                file_path = str(now) + ".wav"  # 音声を保存するファイル名

                wav.setnchannels(af.channels)
                wav.setsampwidth(af.p.get_sample_size(af.format))
                wav.setframerate(af.rate)
                wav.writeframes(b''.join(frames))
                wav.close()
                del frames
                frames = []
                af = AudioFilter()
                # ストリーミングを始める場所
                af.stream.start_stream()

                # 新たに動画ファイルを作成
                writer.release()
                #fps = cnt / rec_time
                print("fpsは"+str(fps))
                writer = cv2.VideoWriter(str(now) + '.mov', fmt, fps, size)

                # 時間リセット
                start = time.time()

                cnt = 0




    # ストリーミングを止める場所
    af.stream.stop_stream()
    af.stream.close()
    af.close()
    # 音声
    # 録音データをファイルに保存
    wav = wave.open(file_path, 'wb')
    wav.setnchannels(af.channels)
    wav.setsampwidth(af.p.get_sample_size(af.format))
    wav.setframerate(af.rate)
    wav.writeframes(b''.join(frames))
    wav.close()
    # 動画終了処理
    writer.release()
    cap.release()
    cv2.destroyAllWindows()