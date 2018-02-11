from aip import AipSpeech
import json
import requests
import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import pygame
import time
import webbrowser

"""音频格式转换"""
def trans_rate(input_file, output_file):
    """参数：输入文件绝对路径，输出文件绝对路径"""
    sound = AudioSegment.from_file(input_file)
    s = sound.set_frame_rate(8000)
    s.export(output_file, format=output_file[-3:])
    
"""录音"""
def recode(output_file):
    """参数：录音文件绝对路径"""
    """阻塞，直到录音完成"""
    CHUNK = 4096  #每次读取的音频流长度
    FORMAT = pyaudio.paInt16  #语音文件的格式
    CHANNELS = 1  #声道数，百度语音识别要求单声道
    RATE = 8000  #采样率， 8000 或者 16000， 推荐 16000 采用率
    wait = True  #录音等待
    LEVEL = 1000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,\
                    frames_per_buffer=CHUNK)
    frames = []
    while wait:
        data = stream.read(CHUNK)
        audio_data = np.fromstring(data, dtype=np.short)
        temp = np.max(audio_data)
        if temp >1500:
            wait = not True
    large_count = np.sum( audio_data > LEVEL )
    while large_count>10:
        frames.append(data) 
        data = stream.read(CHUNK)
        audio_data = np.fromstring(data, dtype=np.short)
        large_count = np.sum( audio_data > LEVEL )
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open('audio/_output_file.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    trans_rate('audio/_output_file.wav', output_file)
    
"""播放WAV"""
def play_wav(file):
    """参数：wav文件绝对路径"""
    """阻塞，直到播放完成"""
    pygame.mixer.init()  #pygame混音器初始化(mixer播放功能很好用)
    mp3 = pygame.mixer.Sound(file)  #加载声音文件
    mp3.play(loops=0)  #播放声音文件，参数：循环次数(其他参数查阅pygame官网)
    while pygame.mixer.get_busy():  #等待音频播放完成
        pass
"""图灵机器人"""
def answer(question):
    """参数：中文问题；返回：JSON格式回答信息"""
    resp = requests.post("http://www.tuling123.com/openapi/api", data={
        #不要用这个key，图灵接口的允许请求次数不多，自己去图灵官网注册用自己的key
        "key": "d59c41e816154441ace453269ea08dba",  
        "info": question,
        "userid": "45879"})  #应该随便取值，图灵承接上下文用的
    return resp.json()

"""以二进制格式打开文件"""
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

"""MP3文件转WAV文件"""
def mp3_to_wav(mp3,wav):
    """参数：MP3文件绝对路径，WAV文件绝对路径"""
    """输出：WAV文件"""
    sound = AudioSegment.from_mp3(mp3)  #加载mp3文件
    sound.export(wav, format="wav")  #转换格式

with open('LoginInfo.txt', 'r') as fp:  #打开LoginInfo.txt
    info = json.loads(fp.read())  #登录信息转换成JSON数据
#根据登录信息创建百度云语音接口，以实现语音识别和语音合成
client = AipSpeech(info['appid'], info['apikey'], info['secretkey'])
while True:
    #等待用户语音输入，阻塞
    recode('audio/man.wav')  
    #得到用户音频百度语音识别结果，返回参数可在百度云语音查看
    result_text = client.asr(get_file_content('audio/man.wav'), 'wav',8000, \
                             { 'lan': 'zh',})
    #判断返回结果中是否含有'result'，含有'result'则为正确返回
    if 'result' in result_text.keys():
        #text是从返回结果提取出的语音识别信息
        text = result_text["result"][0][:-1]
        #得到图灵的返回信息
        turing_answer = answer(text)
        #从图灵的返回信息提取出问题答案
        turing_answer_text = turing_answer['text']
        #判断图灵的返回信息是否含有'url'，搜索图片等会有'url'字段
        if 'url' in turing_answer.keys():
            #打开url
            webbrowser.open(turing_answer['url'])
        #判断图灵的返回信息是否含有'list'，搜索新闻等会有'list'字段
        if 'list' in turing_answer.keys():
            #打开2个url，可以打开很多
            webbrowser.open(turing_answer['list'][0]['detailurl'])
            webbrowser.open(turing_answer['list'][1]['detailurl'])
        #将图灵问题答案变换成音频流
        result  = client.synthesis(turing_answer_text, 'zh', 1,\
                     {'vol': 4,'spd':3,'per':4,'pit':3})
        #将音频写入machine.mp3文件
        if not isinstance(result, dict):  
            with open('audio/machine.mp3', 'wb') as f:
                f.write(result)
        #将machine.mp3转换成machine.wav
        mp3_to_wav('audio/machine.mp3', 'audio/machine.wav')
        #播放machine.wav
        play_wav('audio/machine.wav')
        #避免扬声器余声干扰麦克风造成误触发，此处延时不影响使用体验
        time.sleep(0.1) 
