import cv2
import numpy as np
import datetime
import pyaudio
import wave
import time
import threading
import os

def f():
    ##動画
    count = 0
    diff = 0
    start = time.time()
    global write_flag
    global writer
    while 1:
        if cap.isOpened() and write_flag==False:
            count += 1
            # 音声
            # 動画
            t1 = time.time()
            _, frame = cap.read()
            frame = cv2.resize(frame, size)
            writer.write(frame)
            t2 = time.time() - t1

            #print(t2)

            # 1秒で何フレーム書いたのか計測
            now_time = time.time() - start
            if(now_time > 1.0):
                diff = count - diff
                print("video: time = " + str(now_time),"fps = " + str(diff))
                diff = count
                start = time.time()


            #writerに書き加える処理の時間がバラバラなのでスリープタイムを変動させる
            wait_time = (1/15) - t2
            if(wait_time > 0):
                time.sleep(wait_time)
        else:       #ファイルを生成する。
            # 新たに動画ファイルを作成
            writer.release()
            # fps = cnt / rec_time
            print("fpsは" + str(fps))
            video_file_name = str(now).split(' ')[1] + ".mp4"

            writer = cv2.VideoWriter(video_file_name, fmt, 15, size)

            _, frame = cap.read()
            frame = cv2.resize(frame, size)

            writer.write(frame)

            # 生贄となる音楽ファイルの名前
            str_time_sacrifice = str(pre_time_tmp).split(' ')[1]

            # 最終的に生成する音声つき動画ファイルの名前
            sp1 = str(now).split(' ')[1]
            sp2 = str(sp1).split(':')
            str_time_movie = sp2[0] + "h" + sp2[1] + "m" + str(round(float(sp2[2]))) + "s"

            os.system('ffmpeg -i ./' + str_time_sacrifice + '.mp4 -i ./' + str_time_sacrifice + '.mp3  -vcodec copy -acodec copy ' + str_time_movie + '.mov')

            time.sleep(1/15)
            write_flag = False




            #cv2.imshow('frame', frame)





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

# 時間取得
now = datetime.datetime.now()

rec_time = 30  # 録音時間[s]

frames = []

write_flag = False      #Trueにすると、動画ファイルを区切り、新しく生成する処理に入る

##動画
# 0-4でソースが変わる
cap = cv2.VideoCapture(3)
print(cap.set(cv2.CAP_PROP_FPS, 30))
print(cap.get(cv2.CAP_PROP_FPS))
fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# ソース元のfpsに合わせる必要あり
fps = 30.0
size = (1920, 960)
#size = (640, 360)
video_file_name = str(now).split(' ')[1] + '.mp4'
writer = cv2.VideoWriter(video_file_name, fmt, 15, size)



if __name__ == "__main__":
    # AudioFilterのインスタンスを作る場所
    af = AudioFilter()
    # ストリーミングを始める場所
    af.stream.start_stream()

    file_path = str(now).split(' ')[1] + ".mp3"  # 音声を保存するファイル名

    start = time.time()
    start2 = time.time()        #1sec計測用

    cnt = 0
    i=0

    th = threading.Thread(target=f, name="th", args=())
    # スレッドthの作成 targetで行いたいメソッド,nameでスレッドの名前,argsで引数を指定する
    th.setDaemon(True)
    # thをデーモンに設定する。メインスレッドが終了すると、デーモンスレッドは一緒に終了する
    th.start()
    print("thread start!!")
    # スレッドの開始
    while 1:
        if cap.isOpened():
            # 音声
            # 動画
            #end = time.time()
            now_time = time.time() - start2
            if(now_time > 1.0):
                print(now_time,cnt)
                start2 = time.time()
            #print(end-start)



            if cnt == 0:
                frames = []

            cnt += 1
            sec = int(cnt / fps)
            #print(cnt,"sec=",sec)
            #sec = int(now_time)
            if (sec == rec_time):


                print("はじめ")
                elapsed_time = time.time() - start
                print(cnt,elapsed_time)
                # 時間取得
                pre_time_tmp = now
                now = datetime.datetime.now()
                # 音声
                # ストリーミングを止める場所
                af.stream.stop_stream()
                af.stream.close()
                af.close()
                # 音声
                # 録音データをファイルに保存
                wav = wave.open(file_path, 'wb')
                file_path = str(now).split(' ')[1] + ".mp3"  # 音声を保存するファイル名

                wav.setnchannels(af.channels)
                wav.setsampwidth(af.p.get_sample_size(af.format))
                wav.setframerate(af.rate)
                wav.writeframes(b''.join(frames))
                wav.close()

                write_flag = True       #動画ファイルを書き込む

                del frames
                frames = []
                af = AudioFilter()
                # ストリーミングを始める場所
                af.stream.start_stream()

                # 時間リセット
                start = time.time()

                print("終わり")
                cnt = 0
        time.sleep(1/33)




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