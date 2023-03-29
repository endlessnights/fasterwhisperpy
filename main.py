import requests
from telebot import TeleBot, types
import envparse
import time
import os
from faster_whisper import WhisperModel


envparse.env.read_envfile()
TELEGRAM_BOT_TOKEN: str = envparse.env.str("TELEGRAM_BOT_TOKEN")
bot = TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)


@bot.message_handler(func=lambda message: True, content_types=['voice'])
def text_message(message):
    start_time = time.time()
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    if os.path.isfile('voice.wav'):
        # Delete the file if it exists
        os.remove('voice.wav')
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, file_info.file_path))
    open('voice.ogg', 'wb').write(file.content)

    model_size = "medium"
    model = WhisperModel(model_size, device="cpu", compute_type="float32")
    transcriptionstr = ""
    transcription, info = model.transcribe("voice.ogg", beam_size=5)
    for segment in transcription:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        transcriptionstr += segment.text + " "
    # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    time_exec = "--- %s seconds ---" % (time.time() - start_time)
    texttoreturn = '''
Language: {}
Chance: {}
Text: {}
Time: {}'''
    bot.send_message(chat_id=message.chat.id, text=texttoreturn.format(info.language, info.language_probability, transcriptionstr, time_exec))
    print(transcriptionstr)
    print(time_exec)


bot.polling(none_stop=True)