import random
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Папка с видеофайлами
VIDEO_FOLDER = "videos"

# Функция для создания случайного видео
def create_random_video(output_file):
    # Получаем все видеофайлы из папки
    video_files = [os.path.join(VIDEO_FOLDER, f) for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]

    # Выбираем случайное количество видео
    random_videos = random.sample(video_files, random.randint(2, len(video_files)))

    clips = []
    for video in random_videos:
        clip = VideoFileClip(video)
        # Устанавливаем случайное время воспроизведения для каждого видео
        duration = random.uniform(1, min(clip.duration, 10))  # случайная длина отрезка (1-10 секунд)
        start_time = random.uniform(0, clip.duration - duration)
        clip = clip.subclip(start_time, start_time + duration)
        clips.append(clip)

    # Объединяем все клипы в один
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_file, codec="libx264")

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь /create для создания случайного видео.")

# Функция для создания видео и отправки пользователю
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создаю случайное видео...")

    # Генерация случайного видео
    output_file = "output.mp4"
    create_random_video(output_file)

    # Отправка видео пользователю
    with open(output_file, "rb") as video:
        await update.message.reply_video(video)

# Основная функция запуска бота
async def main():
    bot_token = "7407917160:AAGsC0Fo6tdiHzGXwWG-LKjvUdPEBL1Ipro"  # Замените на токен вашего бота
    application = ApplicationBuilder().token(bot_token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create", create))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())