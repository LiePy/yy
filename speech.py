from aip import AipSpeech
import json

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

with open('LoginInfo.txt', 'r') as fp:  #打开LoginInfo.txt
    info = json.loads(fp.read())  #登录信息转换成JSON数据
client = AipSpeech(info['appid'], info['apikey'], info['secretkey'])  #根据登录信息创建百度云实例

#百度语音识别
all_text = client.asr(get_file_content('audio/audio.wav'), 'pcm', 8000, { 'lan': 'zh',})
text = all_text["result"][0][:-1]
print('语音识别结果：'+text)
#百度语音合成
result  = client.synthesis("系统即将重新启动，请及时备份文件", 'zh', 1, {'vol': 5,})
if not isinstance(result, dict):
    with open('auido.mp3', 'wb') as f:
        f.write(result)
else:
    print('有错误！！！请查看错误码。')

