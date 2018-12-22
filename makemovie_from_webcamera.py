import cv2
import numpy as np
import datetime
import pyaudio
import wave

#時間取得
now = datetime.datetime.now()

rec_time = 10  # 録音時間[s]

class AudioFilter():
    def __init__(self):
        # オーディオに関する設定
        self.p = pyaudio.PyAudio()
        self.channels = 2 # マイクがモノラルの場合は1にしないといけない
        self.rate = 16000 # DVDレベルなので重かったら16000にする
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
        #print(out_data)
        frames.append(out_data)
        return (out_data,pyaudio.paContinue)

    def close(self):
        self.p.terminate()

frames = []

if __name__ == "__main__":
    # AudioFilterのインスタンスを作る場所
    af = AudioFilter()
    # ストリーミングを始める場所
    af.stream.start_stream()

    ## 音声
    # 録音データをファイルに保存
    file_path = str(now) + ".wav"  # 音声を保存するファイル名
    wav = wave.open(file_path, 'wb')
    wav.setframerate(af.rate)
    wav.setnchannels(af.channels)
    wav.setsampwidth(af.p.get_sample_size(af.format))
    wav.setframerate(af.rate)

    ##動画
    cap = cv2.VideoCapture(0)
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    fps = 20
    size = (640, 360)
    writer = cv2.VideoWriter(str(now)+'.mov', fmt, fps, size)

    cnt = 0

    while 1:

        if cap.isOpened():
            # 音声

            # 動画
            _, frame = cap.read()
            frame = cv2.resize(frame, size)
            writer.write(frame)

            cv2.imshow('frame', frame)
            if cv2.waitKey(1) == 13:
                break
            elif cv2.waitKey(1) == 113:
                break

            cnt += 1
            sec = int(cnt / fps)
            if(sec == rec_time):
                print(cnt)
                # 時間取得
                now = datetime.datetime.now()
                # 音声
                file_path = str(now) + ".wav"  # 音声を保存するファイル名
                # ストリーミングを止める場所
                af.stream.stop_stream()
                af.stream.close()
                af.close()
                # 音声
                # 録音データをファイルに保存
                # wav = wave.open(file_path, 'wb')
                # wav.setnchannels(af.channels)
                # wav.setsampwidth(af.p.get_sample_size(af.format))
                # wav.setframerate(af.rate)

                wav.writeframes(b''.join(frames))
                wav.close()

                frames.clear()
                af = AudioFilter()
                # ストリーミングを始める場所
                af.stream.start_stream()
                print(af.channels, af.p.get_sample_size(af.format))

                # 新たに音声ファイルを作成
                file_path = str(now) + ".wav"  # 音声を保存するファイル名
                wav = wave.open(file_path, 'wb')
                wav.setnchannels(af.channels)
                wav.setsampwidth(af.p.get_sample_size(af.format))
                wav.setframerate(af.rate)

                #新たに動画ファイルを作成
                cnt = 0
                writer.release()
                writer = cv2.VideoWriter(str(now) + '.mov', fmt, fps, size)

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