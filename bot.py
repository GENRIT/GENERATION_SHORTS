import telebot
import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip, TextClip
from PIL import Image

# Инициализация бота с вашим токеном
API_TOKEN = '7407917160:AAGsC0Fo6tdiHzGXwWG-LKjvUdPEBL1Ipro'
bot = telebot.TeleBot(API_TOKEN)

# Путь к директории с видео и музыкой
VIDEO_DIR = 'videos'  # В эту папку загружаются видеофайлы
MUSIC_DIR = 'music'   # Папка с музыкой
IMAGE_PATH = 'image/logo.png'  # Путь к логотипу

# Команда start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь команду /create для создания рандомного видео.")

# Команда для создания рандомного видео с текстом
@bot.message_handler(commands=['create'])
def create_random_video(message):
    try:
        # Запрос на получение текста от пользователя
        msg = bot.reply_to(message, "Отправь текст, который ты хочешь добавить к видео:")
        bot.register_next_step_handler(msg, process_text)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

def process_text(message):
    user_text = message.text  # Текст от пользователя
    try:
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(('.mp4', '.avi'))]
        if len(video_files) < 2:
            bot.reply_to(message, "Недостаточно видео для создания.")
            return

        # Рандомно выбираем от 2 до 5 видео
        selected_videos = random.sample(video_files, random.randint(2, 5))
        video_clips = []

        # Для каждого видео выбираем случайное время отрезка для использования и убираем звук
        for video_file in selected_videos:
            clip = VideoFileClip(os.path.join(VIDEO_DIR, video_file)).without_audio()
            max_duration = clip.duration
            start_time = random.uniform(0, max_duration / 2)
            end_time = random.uniform(max_duration / 2, max_duration)
            video_clips.append(clip.subclip(start_time, end_time))

        # Объединяем все клипы в одно видео
        final_clip = concatenate_videoclips(video_clips)

        # Загружаем логотип
        logo = ImageClip(IMAGE_PATH).set_duration(final_clip.duration)
        logo = logo.resize(height=100)  # Увеличить размер логотипа до 100 пикселей
        logo = logo.set_position(("center", "bottom"))

        # Создаём текстовый клип с заданным пользователем текстом
        text_clip = TextClip(user_text, fontsize=24, color='white', bg_color='black', size=final_clip.size)
        text_clip = text_clip.set_duration(final_clip.duration).set_position(("center", "bottom"), y_offset=-110)  # Смещаем над логотипом

        # Наложение логотипа и текста на видео
        final_clip = CompositeVideoClip([final_clip, logo, text_clip])

        # Выбираем случайную музыку из папки MUSIC_DIR
        music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            bot.reply_to(message, "Нет доступных музыкальных файлов.")
            return
        selected_music = random.choice(music_files)
        audio = AudioFileClip(os.path.join(MUSIC_DIR, selected_music)).volumex(0.1)  # Уменьшаем громкость до 10%
        audio = audio.subclip(0, final_clip.duration)

        # Добавляем аудио к видео
        final_clip = final_clip.set_audio(audio)

        # Сохраняем итоговое видео
        output_path = os.path.join(VIDEO_DIR, 'output.mp4')
        final_clip.write_videofile(output_path)

        # Отправляем готовое видео
        with open(output_path, 'rb') as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Запуск бота
bot.polling()
