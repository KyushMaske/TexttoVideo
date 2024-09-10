
from moviepy.editor import concatenate_videoclips, VideoFileClip, concatenate_audioclips, AudioFileClip
from tools import text_to_audio, get_keywords_from_text, keywords_to_images, images_to_video, merge_audio_video, get_corner_video, add_corner_video, merge_all_clips
import os
import statistics

from logging_config import setup_logging
import logging

# Configure logging
setup_logging()


def merge_audios_in_folder(input_folder, output_file):
    audio_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.mp3')])
    audio_clips = [AudioFileClip(f) for f in audio_files]
    final_clip = concatenate_audioclips(audio_clips)
    output_path = os.path.join(input_folder, output_file)
    final_clip.write_audiofile(output_path)
    logging.info(f"All audios merged into: {output_path}")

    # Clean up audio files except the final combined audio
    for file in audio_files:
        if file != output_path:
            try:
                os.remove(file)
                logging.info(f"Deleted: {file}")
            except Exception as e:
                logging.info(f"Error while deleting {file}: {e}")

def merge_videos_in_folder(input_folder, output_file):
    video_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.mp4')])
    video_clips = [VideoFileClip(os.path.join(input_folder, f)) for f in video_files]
    final_clip = concatenate_videoclips(video_clips)
    final_clip.write_videofile(output_file, fps=24)
    logging.info(f"All videos merged into: {output_file}")

def create_videos_from_article(article_text, output_dir="output_videos"):
    texts = article_text.split(".")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ALL_CLIPS = []
    ALL_AUDIOS = []
    
    for i, text in enumerate(texts):
        if len(text.strip()) < 5:
            continue
        
        text = text.strip()
        logging.info(f"Processing text {i+1}: {text}")
        
        keywords = get_keywords_from_text(text)
        # keywords = [keyword for keyword, chances in keywords if chances > 0.4]
        chances = [chance for keyword, chance in keywords]
        mean_chance = statistics.mean(chances)
        logging.info(f"Mean chance: {mean_chance}")

        # Select only those keywords whose chances are greater than the mean
        keywords = [keyword for keyword, chance in keywords if chance > mean_chance]
        
        audio = text_to_audio(text)
        audio_duration = audio.duration
        
        logging.info(f"Audio duration: {audio_duration}")
        logging.info(f"Keywords: {keywords}")
        
        images = keywords_to_images(keywords)
        logging.info(f"Images: {images}")
        
        video = images_to_video(images, audio_duration)
        video = merge_audio_video(audio, video)
        
        output_video_path = os.path.join(output_dir, f"video_{i+1}.mp4")
        video.write_videofile(output_video_path, fps=24)
        
        logging.info(f"Video saved to: {output_video_path}")
        ALL_CLIPS.append(video)
        
        # Clean up images
        for image in images:
            try:
                os.remove(image)
            except Exception as e:
                logging.info(f"Error while deleting image {image}: {e}")

    # Merge all clips into one final video
    if ALL_CLIPS:
        final_video_path = os.path.join(output_dir, "final_video.mp4")
        concatenated_clip = concatenate_videoclips(ALL_CLIPS)
        concatenated_clip.write_videofile(final_video_path, fps=24)
        logging.info(f"All clips merged into: {final_video_path}")
    else:
        logging.info("No valid clips to merge.")

    # Handle empty text case by merging all videos in output folder
    if not any(text.strip() for text in texts):
        merge_videos_in_folder(output_dir, os.path.join(output_dir, "combined_videos.mp4"))


    for file in os.listdir(output_dir):
        if file.endswith(".mp4"):
            if file != "final_video.mp4" and file != "combined_videos.mp4":
                try:
                    os.remove(os.path.join(output_dir, file))
                    logging.info(f"Deleted: {file}")
                except Exception as e:
                    logging.info(f"Error while deleting {file}: {e}")

if __name__ == "__main__":
    # ARTICLE = """Personality deficiency is a complex and multifaceted issue that affects various aspects of an individual's life, from personal relationships to professional success. Understanding its causes, manifestations, and impacts is crucial for developing empathy and effective support mechanisms. Through therapeutic interventions, social support, and personal development, individuals can overcome the challenges associated with personality deficiencies and lead fulfilling, meaningful lives. Addressing this issue requires a collective effort, emphasizing the importance of compassion, understanding, and proactive support for those affected. """
    ARTICLE = """The Rise of Nepal Cricket: A Journey of Passion and Perseverance

Nepal, a nation nestled in the lap of the Himalayas, is renowned for its breathtaking landscapes and rich cultural heritage. In recent years, however, it has also gained recognition in the world of cricket. The journey of Nepal Cricket is a testament to the spirit of resilience and passion that defines this nation.

Cricket in Nepal began its journey in the early 20th century, introduced by the ruling Rana dynasty who were influenced by the British. However, it wasn't until the 1990s that cricket started gaining significant traction among the Nepali populace. The establishment of the Cricket Association of Nepal (CAN) in 1946 and its affiliation with the International Cricket Council (ICC) in 1996 marked the beginning of Nepal's formal cricketing journey.
"""
    input_folder = "audio"
    output_file = "combined_audio.mp3"
    create_videos_from_article(ARTICLE)
    merge_audios_in_folder(input_folder, output_file)


