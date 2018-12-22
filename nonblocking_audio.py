
import pyaudio
import time
import datetime
import wave
frames= []
#時間取得
now = datetime.datetime.now()
file_path = str(now)+".wav"  # 音声を保存するファイル名

class AudioFilter():
    def __init__(self):
        # オーディオに関する設定
        self.p = pyaudio.PyAudio()
        self.channels = 2 # マイクがモノラルの場合は1にしないといけない
        self.rate = 24000 # DVDレベルなので重かったら16000にする
        self.format = pyaudio.paInt16
        self.chunk = 1024
        self.stream = self.p.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        output=True,
                        input=True,
                        frames_per_buffer=self.chunk,
                        stream_callback=self.callback)

    # コールバック関数（再生が必要なときに呼び出される）
    def callback(self, in_data, frame_count, time_info, status):
        out_data = in_data
        # data = self.stream.read(self.chunk)
        #print(out_data)
        frames.append(out_data)
        return (out_data, pyaudio.paContinue)

    def close(self):
        self.p.terminate()

if __name__ == "__main__":
    # AudioFilterのインスタンスを作る場所
    af = AudioFilter()

    # ストリーミングを始める場所
    af.stream.start_stream()
    cnt = 0
    # ノンブロッキングなので好きなことをしていていい場所
    while af.stream.is_active():
        if(cnt == 30):
            # 時間取得
            now = datetime.datetime.now()
            file_path = str(now) + ".wav"  # 音声を保存するファイル名
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

            af = AudioFilter()
            # ストリーミングを始める場所
            af.stream.start_stream()
            print(af.channels,af.p.get_sample_size(af.format))
            cnt = 0
            #break
        cnt += 1
        time.sleep(0.1)

    # ストリーミングを止める場所
    af.stream.stop_stream()
    af.stream.close()
    af.close()
    #音声
    # 録音データをファイルに保存
    wav = wave.open(file_path, 'wb')
    wav.setnchannels(af.channels)
    wav.setsampwidth(af.p.get_sample_size(af.format))
    wav.setframerate(af.rate)
    wav.writeframes(b''.join(frames))
    wav.close()