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
    def __init__(self,name=['小明'],per=1,speed=5,pit=5,vol=5,listen_time=5):
        self.name = name
        self.speed = speed
        self.per = per
        self.pit = pit
        self.vol = vol
        self.listen_time = listen_time
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
        self.test = True
        
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
        CHUNK = 1024
        wf = wave.open(file, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        
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
                info = result_text["result"][0][:-1]
                if self.test:
                    print('唤醒音识别结果：'+info)
                if info in self.name:
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
                if self.nowtime-self.starttime>self.listen_time:
                    self.listen = True
                    self.work = not True
                    self.stop = not True
                    self.play_wav(self.stop_wav)
                    break
            if self.work:
                large_count = np.sum( audio_data > LEVEL )
                while large_count>8:
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
                    if self.test:
                        print('语音输入识别结果：'+self.questen)
                    if self.questen in ['机电了','点了','机电','电缆','电了','现在几点了']:#对时间的处理，‘几点了’的识别结果很无奈
                        now_time = time.localtime()
                        tm_hour = now_time.tm_hour
                        if tm_hour >= 12:
                            tm_hour -= 12
                        tm_min = now_time.tm_min
                        tm_sec = now_time.tm_sec
                        turing_answer_text = str(tm_hour)+'点'+str(tm_min)+'分'+str(tm_sec)+'秒'
                    elif self.questen in ['今天几号','今天多少号']:#对日期的处理
                        now_time = time.localtime()
                        tm_mon = now_time.tm_mon
                        tm_mday = now_time.tm_mday
                        turing_answer_text = str(tm_mon)+'月'+str(tm_mday)+'号'
                    elif self.questen in ['今天星期几']:#对星期的处理
                        now_time = time.localtime()
                        tm_wday = now_time.tm_wday+1
                        if tm_wday <= 6:
                            turing_answer_text = '星期'+str(tm_wday)
                        else:
                            turing_answer_text = '星期日'
                    elif self.questen in ['唱首歌']:#对唱歌的处理
                        turing_answer_text = '走开，我是不会给你唱歌的'
                    else:
                        turing_answer = self.answer()
                        turing_answer_text = turing_answer['text']
                        if 'url' in turing_answer.keys():
                            webbrowser.open(turing_answer['url'])
                        if 'list' in turing_answer.keys():
                            webbrowser.open(turing_answer['list'][0]['detailurl'])
                            webbrowser.open(turing_answer['list'][1]['detailurl'])
                    if self.test:
                        print('图灵机器人的回答：'+turing_answer_text)
                    result  = self.client.synthesis(turing_answer_text, 'zh', 1,{'vol':self.vol,'spd':self.speed,'per':self.per,'pit':self.pit})
                    if not isinstance(result, dict):  
                        with open(self.machine_mp3, 'wb') as f:
                            f.write(result)
                    self.mp3_to_wav(self.machine_mp3, self.machine_wav)
                    self.play_wav(self.machine_wav)
                    time.sleep(0.1)
                    self.starttime = time.time()
    def run(self):
        self.login()
        while True:
            self.listening()
            self.working()

