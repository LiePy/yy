# 语音实时对话机器人
 **简介：** 

结合百度语音识别，图灵机器人和百度语音合成实现的实时对话机器人，相较[第一版树莓派实时对话机器人](http://blog.csdn.net/lingdongtianxia/article/details/54799306)反应速度，使用体验有很大提升。现在这个机器人支持搜索图片、火车票、新闻和菜谱等。具体功能详见图灵官网。

 **文件结构:** 
```
|——audio
|  |——_output_file.wav  #录音时的音频缓冲文件
|  |——man.wav  #录音文件，说话的声音信息在这里面
|  |——machine.mp3  #百度语音合成返回的MP3文件
|  |——machine.wav  #MP3文件转码后的WAV格式音频文件
|——ffmpeg.exe  #安装pydub后需要将这个文件放在windows系统的环境变量里面，也可以为了省事把它和pip放在一起
|——LoginInfo.txt  #百度云语音识别登录信息，自己注册百度云账号得到自己的登录信息
|——speech.py  #语音对话主程序
```
 **链接：** 

[百度云登录](https://login.bce.baidu.com/)

[图灵机器人官网](http://www.tuling123.com/)

[ffmpeg.exe下载](http://download.csdn.net/download/lingdongtianxia/10249402)

[pygame文档](http://pygame.org/docs/)

 **环境及安装方法：**
```
版本：
    windows10 、python3.6
相关库（Linux安装需要管理员权限）：
    pydub 安装方法 1、pip install pydub  2、将ffmpeg.exe路径加入windows系统环境变量，Linux可能直接pip就可以了，我没试
    aip   安装方法 pip install baidu-aip
    别的库自己缺什么pip install什么吧，Linux别忘了权限问题
```

