import telebot
import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip, TextClip
from PIL import Image
import conf  # Импортируем конфигурации

# Инициализация бота с вашим токеном из conf.py
bot = telebot.TeleBot(conf.API_TOKEN)

# Команда start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь команду /create для создания рандомного видео и укажи текст в формате: /create твой_текст.")

# Команда для создания рандомного видео
@bot.message_handler(commands=['create'])
def create_random_video(message):
    try:
        video_files = [f for f in os.listdir(conf.VIDEO_DIR) if f.endswith(('.mp4', '.avi'))]
        if len(video_files) < 2:
            bot.reply_to(message, "Недостаточно видео для создания.")
            return

        selected_videos = random.sample(video_files, random.randint(2, 5))
        video_clips = []

        for video_file in selected_videos:
            clip = VideoFileClip(os.path.join(conf.VIDEO_DIR, video_file)).without_audio()
            max_duration = clip.duration
            start_time = random.uniform(0, max_duration / 2)
            end_time = random.uniform(max_duration / 2, max_duration)
            video_clips.append(clip.subclip(start_time, end_time))

        final_clip = concatenate_videoclips(video_clips)

        # Загружаем логотип
        logo = ImageClip(conf.IMAGE_PATH).set_duration(final_clip.duration)
        logo = logo.resize(height=100)
        logo = logo.set_position(("center", "bottom"))

        final_clip = CompositeVideoClip([final_clip, logo])

        user_text = message.text.replace("/create ", "")

        # Создаем текстовый клип с пользовательскими настройками
        text_clip = TextClip(user_text, fontsize=conf.TEXT_SIZE, color=conf.TEXT_COLOR, font=conf.TEXT_FONT).set_duration(final_clip.duration)
        text_clip = text_clip.set_position(("center", "top"))

        final_clip = CompositeVideoClip([final_clip, text_clip])

        music_files = [f for f in os.listdir(conf.MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            bot.reply_to(message, "Нет доступных музыкальных файлов.")
            return

        selected_music = random.choice(music_files)
        audio = AudioFileClip(os.path.join(conf.MUSIC_DIR, selected_music)).volumex(conf.MUSIC_VOLUME)

        audio = audio.subclip(0, final_clip.duration)

        final_clip = final_clip.set_audio(audio)

        output_path = os.path.join(conf.VIDEO_DIR, 'output.mp4')
        final_clip.write_videofile(output_path)

        with open(output_path, 'rb') as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Запуск бота
bot.polling()
