from aip import AipSpeech
import json
import requests
import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import time
import webbrowser
class Family():
    def __init__(self,name,speed):
        self.name = name
        self.speed = speed
        self._output_file = 'audio/_output_file.wav'
        self.man_wav = 'audio/man.wav'
        self.machine_mp3 = 'audio/machine.mp3'
        self.machine_wav = 'audio/machine.wav'
        self.start_wav = 'audio/start.wav'
        self.sleep_wav = 'audio/sleep.wav'
        self.stop_wav = 'audio/stop.wav'
        self.questen = ''
        self.client = None
        self.listen = True
        self.work = not True
        self.stop = not True
        self.starttime = 0
        self.nowtime = 0
        
    """以二进制格式打开文件"""
    def get_file_content(self,filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
        
    """音频格式转换"""
    def trans_rate(self,input_file, output_file):
        """参数：输入文件绝对路径，输出文件绝对路径"""
        sound = AudioSegment.from_file(input_file)
        s = sound.set_frame_rate(8000)
        s.export(output_file, format=output_file[-3:])

    """播放WAV"""
    def play_wav(self,file):
        """参数：wav文件绝对路径"""
        """阻塞，直到播放完成"""
        pygame.mixer.init()  #pygame混音器初始化(mixer播放功能很好用)
        mp3 = pygame.mixer.Sound(file)  #加载声音文件
        mp3.play(loops=0)  #播放声音文件，参数：循环次数(其他参数查阅pygame官网)
        while pygame.mixer.get_busy():  #等待音频播放完成
            pass
        
    """图灵机器人"""
    def answer(self):
        """参数：中文问题；返回：JSON格式回答信息"""
        resp = requests.post("http://www.tuling123.com/openapi/api", data={
            #不要用这个key，图灵接口的允许请求次数不多，自己去图灵官网注册用自己的key
            "key": "d59c41e816154441ace453269ea08dba",  
            "info": self.questen,
            "userid": "45879"})  #应该随便取值，图灵承接上下文用的
        return resp.json()

    """MP3文件转WAV文件"""
    def mp3_to_wav(self,mp3,wav):
        """参数：MP3文件绝对路径，WAV文件绝对路径"""
        """输出：WAV文件"""
        sound = AudioSegment.from_mp3(mp3)  #加载mp3文件
        sound.export(wav, format="wav")  #转换格式
    
    """有声音就录音"""
    def recodeing(self):
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
        wf = wave.open(self._output_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.trans_rate(self._output_file, self.man_wav)
    def login(self):
        with open('LoginInfo.txt', 'r') as fp:  #打开LoginInfo.txt
            info = json.loads(fp.read())  #登录信息转换成JSON数据
        #根据登录信息创建百度云语音接口，以实现语音识别和语音合成
        self.client = AipSpeech(info['appid'], info['apikey'], info['secretkey'])
    def listening(self):
        while self.listen:
            self.recodeing()
            result_text = self.client.asr(self.get_file_content(self.man_wav), 'wav',8000, { 'lan': 'zh',})
            if 'result' in result_text.keys():
                if result_text["result"][0][:-1] == self.name:
                    self.listen = not True
                    self.work = True
                    self.stop = not True
                    break
    def working(self):
        self.play_wav(self.start_wav)
        self.starttime = time.time()
        while self.work:
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
                    break
                self.nowtime = time.time()
                if self.nowtime-self.starttime>10:
                    self.listen = True
                    self.work = not True
                    self.stop = not True
                    self.play_wav(self.sleep_wav)
                    break
            if self.work:
                large_count = np.sum( audio_data > LEVEL )
                while large_count>10:
                    frames.append(data) 
                    data = stream.read(CHUNK)
                    audio_data = np.fromstring(data, dtype=np.short)
                    large_count = np.sum( audio_data > LEVEL )
                stream.stop_stream()
                stream.close()
                p.terminate()
                wf = wave.open(self._output_file, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                self.trans_rate(self._output_file, self.man_wav)
                #录音结束
                result_text = self.client.asr(self.get_file_content(self.man_wav), 'wav',8000, { 'lan': 'zh',})
                if 'result' in result_text.keys():
                    self.questen = result_text["result"][0][:-1]
                    turing_answer = self.answer()
                    turing_answer_text = turing_answer['text']
                    if 'url' in turing_answer.keys():
                        webbrowser.open(turing_answer['url'])
                    if 'list' in turing_answer.keys():
                        webbrowser.open(turing_answer['list'][0]['detailurl'])
                        webbrowser.open(turing_answer['list'][1]['detailurl'])
                    result  = self.client.synthesis(turing_answer_text, 'zh', 1,\
                                 {'vol': 4,'spd':self.speed,'per':4,'pit':3})
                    if not isinstance(result, dict):  
                        with open(self.machine_mp3, 'wb') as f:
                            f.write(result)
                    self.mp3_to_wav(self.machine_mp3, self.machine_wav)
                    self.play_wav(self.machine_wav)
                    time.sleep(0.1)
                    self.starttime = time.time()
    def run(self):
        while True:
            self.listening()
            self.working()

