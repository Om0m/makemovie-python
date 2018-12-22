# coding:utf-8
from __future__ import division
import wave
import numpy as np
import scipy.io.wavfile
import scipy.signal
import pylab as P

"""Qiitaの参照記事から引用"""
def autocorr(x, nlags=None):
    """自己相関関数を求める
    x:     信号
    nlags: 自己相関関数のサイズ（lag=0からnlags-1まで）
           引数がなければ（lag=0からlen(x)-1まですべて）
    """
    N = len(x)
    if nlags == None: nlags = N
    r = np.zeros(nlags)
    for lag in range(nlags):
        for n in range(N - lag):
            r[lag] += x[n] * x[n + lag]
    return r

def LevinsonDurbin(r, lpcOrder):
    """Levinson-Durbinのアルゴリズム
    k次のLPC係数からk+1次のLPC係数を再帰的に計算して
    LPC係数を求める"""
    # LPC係数（再帰的に更新される）
    # a[0]は1で固定のためlpcOrder個の係数を得るためには+1が必要
    a = np.zeros(lpcOrder + 1)
    e = np.zeros(lpcOrder + 1)

    # k = 1の場合
    a[0] = 1.0
    a[1] = - r[1] / r[0]
    e[1] = r[0] + r[1] * a[1]
    lam = - r[1] / r[0]

    # kの場合からk+1の場合を再帰的に求める
    for k in range(1, lpcOrder):
        # lambdaを更新
        lam = 0.0
        for j in range(k + 1):
            lam -= a[j] * r[k + 1 - j]
        lam /= e[k]

        # aを更新
        # UとVからaを更新
        U = [1]
        U.extend([a[i] for i in range(1, k + 1)])
        U.append(0)

        V = [0]
        V.extend([a[i] for i in range(k, 0, -1)])
        V.append(1)

        a = np.array(U) + lam * np.array(V)

        # eを更新
        e[k + 1] = e[k] * (1.0 - lam * lam)

    return a, e[-1]
"""LPCスペクトル包絡を求める"""

def wavread(filename):
    wf = wave.open(filename, "r")
    fs = wf.getframerate()
    x = wf.readframes(wf.getnframes())
    x = np.frombuffer(x, dtype="int16") / 32768.0  # (-1, 1)に正規化
    wf.close()
    return x, float(fs)

def preEmphasis(signal, p):
    """プリエンファシスフィルタ"""
    # 係数 (1.0, -p) のFIRフィルタを作成
    return scipy.signal.lfilter([1.0, -p], 1, signal)

def plot_signal(s, a, e, fs, lpcOrder, file):
    t = np.arange(0.0, len(s) / fs, 1/fs)
    # LPCで前向き予測した信号を求める
    predicted = np.copy(s)
    # 過去lpcOrder分から予測するので開始インデックスはlpcOrderから
    # それより前は予測せずにオリジナルの信号をコピーしている
    for i in range(lpcOrder, len(predicted)):
        predicted[i] = 0.0
        for j in range(1, lpcOrder):
            predicted[i] -= a[j] * s[i - j]
    # オリジナルの信号をプロット
    P.plot(t, s)
    # LPCで前向き予測した信号をプロット
    P.plot(t, predicted,"r",alpha=0.4)
    P.xlabel("Time (s)")
    P.xlim((-0.001, t[-1]+0.001))
    P.title(file)
    P.grid()
    P.show()
    return 0

def plot_spectrum(s, a, e, fs, file):
    # LPC係数の振幅スペクトルを求める
    nfft = 2048   # FFTのサンプル数
    fscale = np.fft.fftfreq(nfft, d = 1.0 / fs)[:int(nfft/2)]
    # オリジナル信号の対数スペクトル
    spec = np.abs(np.fft.fft(s, nfft))
    logspec = 20 * np.log10(spec)
    P.plot(fscale, logspec[:int(nfft/2)])
    # LPC対数スペクトル
    w, h = scipy.signal.freqz(np.sqrt(e), a, nfft, "whole")
    lpcspec = np.abs(h)
    loglpcspec = 20 * np.log10(lpcspec)
    P.plot(fscale, loglpcspec[:int(nfft/2)], "r", linewidth=2)
    P.xlabel("Frequency (Hz)")
    P.xlim((-100, 8100))
    P.title(file)
    P.grid()
    P.show()
    return 0

def lpc_spectral_envelope(file):
    # 音声をロード
    wav, fs = wavread(file)
    t = np.arange(0.0, len(wav) / fs, 1/fs)
    # 音声波形の中心部分を切り出す
    center = len(wav) / 2  # 中心のサンプル番号
    cuttime = 0.04         # 切り出す長さ [s]
    print(center - cuttime/2*fs,center + cuttime/2*fs)
    s = wav[int(center - cuttime/2*fs) : int(center + cuttime/2*fs)]
    # プリエンファシスフィルタをかける
    p = 0.97         # プリエンファシス係数
    s = preEmphasis(s, p)
    # ハミング窓をかける
    hammingWindow = np.hamming(len(s))
    s = s * hammingWindow
    # LPC係数を求める
#    lpcOrder = 12
    lpcOrder = 32
    r = autocorr(s, lpcOrder + 1)
    a, e  = LevinsonDurbin(r, lpcOrder)
    print("a",a)
    #polesには複素数が入る
    poles = np.roots(a)
    intns = np.abs(poles)
    print("intns",np.angle(intns))
    ff = np.angle(poles) * fs / 2.0 / np.pi
    print("ff",ff)
    formantfreq = ff[(ff > 10) & (ff < fs / 2.0 - 10) & (intns > 0.8)]
    print("formant=",formantfreq)
    plot_signal(s, a, e, fs, lpcOrder, file)
    plot_spectrum(s, a, e, fs, file)
    return 0

if __name__ == "__main__":
    file = "a.wav"
    lpc_spectral_envelope(file)
    exit(0)