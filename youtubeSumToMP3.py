import pyttsx3
import yt_dlp
import openai
import datetime
from pydub import AudioSegment
import os

# 填入影片的URL
url = 'https://youtu.be/'
TOKEN = ""
date = str(datetime.date.today())
download_path = r"D:\Dropbox\Music" + "\\" + date

def mp3(text,filename):
    #查出來念中文是哪個機碼ID
    zh_voiceid = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-TW_HANHAN_11.0'
    engine= pyttsx3.init()
    #設定念中文
    engine.setProperty('voice',zh_voiceid) 
    #設定語速
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate+15)
    engine.save_to_file(text, filename)
    engine.runAndWait()


# 設定選項
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl':'/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


# 建立 yt_dlp 下載器物件
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # 下載影片
    info_dict = ydl.extract_info(url, download=True)
    # 得到影片標題
    video_title = info_dict.get('title', None)



# 載入 MP3 音檔
sound = AudioSegment.from_file(video_title + ".mp3", format='mp3')
# 設定每個分割檔案的長度（單位：毫秒）
segment_length = 1000000
# 將音檔分割成多個檔案，並進行轉譯文字
transcript_ary = []
for i, chunk in enumerate(sound[::segment_length]):
    # 設定分割檔案的檔名
    chunk.export(f'output_{i}.mp3', format='mp3')
    # 轉譯文字
    openai.api_key = TOKEN 
    audio_file = open(f'output_{i}.mp3', "rb")
    transcript_ary.append(openai.Audio.transcribe("whisper-1", audio_file).to_dict().get('text'))
# 合併所有轉譯文字 將list用空白合併成一個String
transcript = ' '.join(transcript_ary)
transcript_list = []
ret = ''
for script in transcript.split():
    ret = ret + ' ' + script
    if len(ret) > 1000:
        transcript_list.append(ret)
        ret = ''
transcript_list.append(ret)

# for t in transcript_list:   
#     print(t)

#進行摘要
#ChatCompletion 使用方式請參考 "platform.openai.com/docs/api-reference/chat/create"
result_ary = []
openai.api_key = TOKEN 
for t in transcript_list:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "請你成為文章摘要的小幫手，摘要以下文字，以繁體中文輸出"},
        {"role": "user", "content": t}
      ]
    )
    # result_ary.append(response.choices[0].message)
    result_ary.append(response['choices'][0]['message'])
#print(result_ary[0].get('content'))

text = ""
for res in result_ary:
    # print(res.get('content'))
    text = text + "  " + res.get('content')

#print(text)

def main():
    mp3(text,download_path + "\\" + video_title + ".mp3")
    print("摘要完成!")
    os.remove(video_title + ".mp3")
    
if __name__ == "__main__":
    main()
