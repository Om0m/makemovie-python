#coding:utf-8
import wave
import pyaudio
import struct
from pylab import *
import numpy as np

def play(data, fs, bit):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=int(fs),
                    output=True)
    # 再生
    chunk = 1024
    sp = 0
    buffer = data[sp:sp+chunk]
    while stream.is_active():
        stream.write(buffer)
        sp += chunk
        buffer = data[sp:sp+chunk]
        if buffer == b'': stream.stop_stream()
    stream.close()
    p.terminate()
    return p

def distortion(data, gain, level):
    length = len(data)
    newdata = [0.0] * length
    for n in range(length):
        newdata[n] = data[n] * gain  # 増幅
        # クリッピング
        if newdata[n] > 1.0:
            newdata[n] = 1.0
        elif newdata[n] < -1.0:
            newdata[n] = -1.0
        # 音量を調整
        newdata[n] *= level
    return newdata

def save(data, fs, bit, filename,p):
    """波形データをWAVEファイルへ出力"""
    fmt = pyaudio.paInt16

    wf = wave.open(filename, "w")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(fmt))
    wf.setframerate(fs)
    wf.writeframes(data)
    wf.close()

if __name__ == "__main__":
    # 音声をロード
    wf = wave.open("output.wav")
    fs = wf.getframerate()
    length = wf.getnframes()
    data = wf.readframes(length)

    # # デフォルトの音声を再生、ファイルにも保存
    # play(data, fs, 16)
    # save(data, fs, 16, "original.wav")

    # エフェクトをかけやすいようにバイナリデータを[-1, +1]に正規化
    data = np.frombuffer(data, dtype="int16") / 32768.0

    # オリジナル波形の一部をプロット
    figure(1)
    subplot(211)
    plot(data)
    xlabel("time [sample]")
    ylabel("amplitude")
    ylim([-1.0, 1.0])

    # ここでサウンドエフェクト
    newdata = distortion(data, 20, 0.3)

    # サウンドエフェクトをかけた波形の一部をプロット
    print(newdata[0:2000])
    subplot(212)
    plot(newdata)
    xlabel("time [sample]")
    ylabel("amplitude")
    ylim([-1.0, 1.0])


    ### 元の波形をスペクトログラム表示
    figure(2)
    length_sec = float(wf.getnframes()) / wf.getframerate()  # 波形長さ（秒）
    # FFTのサンプル数 一度の窓幅のサンプル数を大きくすると、周波数分解能が上がり、時間分解能が下がる
    N = 1024
    # FFTで用いるハミング窓
    hammingWindow = np.hamming(N)
    # スペクトログラムを描画
    subplot(211)
    pxx, freqs, bins, im = specgram(data, NFFT=N, Fs=wf.getframerate(), noverlap=0, window=hammingWindow)
    axis([0, length_sec, 0, wf.getframerate() / 8])
    xlabel("time [second]")
    ylabel("frequency [Hz]")

    ### エフェクトを掛けた後の波形をスペクトログラム表示
    length_sec = float(wf.getnframes()) / wf.getframerate()  # 波形長さ（秒）
    # FFTのサンプル数
    N = 1024
    # FFTで用いるハミング窓
    hammingWindow = np.hamming(N)
    # スペクトログラムを描画
    subplot(212)
    pxx, freqs, bins, im = specgram(newdata, NFFT=N, Fs=wf.getframerate(), noverlap=0, window=hammingWindow)
    axis([0, length_sec, 0, wf.getframerate() / 8])
    xlabel("time [second]")
    ylabel("frequency [Hz]")

    # 正規化前のバイナリデータに戻す
    newdata = [int(x * 32767.0) for x in newdata]
    newdata = struct.pack("h" * len(newdata), *newdata)

    # サウンドエフェクトをかけた音声を再生
    p = play(newdata, fs, 16)
    save(newdata, fs, 16, "distortion.wav",p)
    warnings.filterwarnings("ignore", category=mpl.cbook.MatplotlibDeprecationWarning)

    show()
