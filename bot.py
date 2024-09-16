import telebot
import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip
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

# Команда для создания рандомного видео
@bot.message_handler(commands=['create'])
def create_random_video(message):
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
            # Обрезаем видео по случайным временам
            video_clips.append(clip.subclip(start_time, end_time))
        
        # Объединяем все клипы в одно видео
        final_clip = concatenate_videoclips(video_clips)
        
        # Загружаем логотип
        logo = ImageClip(IMAGE_PATH).set_duration(final_clip.duration)
        
        # Устанавливаем позицию логотипа (центр снизу)
        logo = logo.resize(height=50)  # Изменить размер логотипа
        logo = logo.set_position(("center", "bottom"))
        
        # Наложение логотипа на видео
        final_clip = CompositeVideoClip([final_clip, logo])
        
        # Выбираем случайную музыку из папки MUSIC_DIR
        music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            bot.reply_to(message, "Нет доступных музыкальных файлов.")
            return
        
        selected_music = random.choice(music_files)
        audio = AudioFileClip(os.path.join(MUSIC_DIR, selected_music)).volumex(0.1)  # Уменьшаем громкость до 10%
        
        # Обрезаем аудио до длины видео
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
