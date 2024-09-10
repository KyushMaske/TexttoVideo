from importlib.resources import path
import pyttsx3
import pixabay.core
from moviepy import *
from moviepy.editor import *
from keybert import KeyBERT
import random
import os
import time
import numpy as np

from logging_config import setup_logging
import logging

# Configure logging
setup_logging()


px = pixabay.core("20484832-b73e12f8e2c1f4f9b0ae74bac")
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
kw_model = KeyBERT()

def text_to_audio(text):
    time.sleep(1)
    audio_file = f"./audio/{text[0:10]}--{len(text)}.mp3"
    logging.info("Converting text to audio...")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 135)
    engine.setProperty('volume', 1)
    engine.save_to_file(f"<pitch middle='-100'>{text}.</pitch>", audio_file)
    engine.runAndWait()
    return AudioFileClip(audio_file)




def get_keywords_from_text(text):
    logging.info("Getting keywords from text...")
    # kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text)
    logging.info(f"Keywords Keywords Keywords get_keywords_from_text: {keywords}")
    # random.shuffle(keywords)
    return keywords


from PIL import Image

def keywords_to_images(keywords):
    IMAGES = []
    for keyword in keywords:
        logging.info(f"Getting images for keyword: {keyword}")
        try:
            images = px.query(keyword)
            images = [images[i] for i in range(min(20, len(images)))]
            random.shuffle(images)
            logging.info(f"{len(images)} images found")
            for i in range(0, min(3, len(images))):
                path = f"./images/{keyword}{i}.jpg"
                images[i].download(path, "largeImage")
                IMAGES.append(path)
                # Convert to RGB and resize if needed
                img = Image.open(path)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img = img.resize((480, 360))
                img.save(path)  # Save back as JPEG after resizing
        except Exception as e:
            logging.info(f"Error getting images for keyword {keyword}: {e}")
    return IMAGES


# def images_to_video(images, seconds):
#     clips = []
#     for image in images:
#         clips.append(ImageClip(image).set_duration(seconds / max(random.randint(2, 5), len(images))))
#     clips = [clip.resize((480, 360)) for clip in clips]
#     clips = [clip.resize(lambda t: 1 + 0.2 * t) for clip in clips]
#     clip = concatenate_videoclips(clips=clips, method='compose')
#     return clip

# import requests
# import random
# from PIL import Image
# from io import BytesIO

# def keywords_to_images(keywords):
#     IMAGES = []
#     base_url = "https://api.unsplash.com/photos/random"
#     access_key = "3B16Dmtd6bsFJMSTKrXsrooJFR2DG4_z0SQBcEqqC4A"  # Replace with your actual Unsplash access key

#     headers = {
#         "Authorization": f"Client-ID {access_key}"
#     }

#     for keyword in keywords:
#         logging.info(f"Getting images for keyword: {keyword}")
#         try:
#             params = {
#                 "query": keyword,
#                 "count": 3  # Number of images per keyword
#             }
#             response = requests.get(base_url, headers=headers, params=params)
#             images_data = response.json()

#             for idx, img_data in enumerate(images_data):
#                 img_url = img_data['urls']['raw']
#                 img_response = requests.get(img_url)
#                 img = Image.open(BytesIO(img_response.content))
                
#                 # Resize if needed
#                 img = img.resize((480, 360))

#                 # Save the image
#                 path = f"./images/{keyword}_{idx}.jpg"
#                 img.save(path, format="JPEG")
#                 IMAGES.append(path)

#         except Exception as e:
#             logging.info(f"Error getting images for keyword {keyword}: {e}")

#     return IMAGES



def images_to_video(images, duration):
    clips = []
    for image in images:
        img = Image.open(image)
        if img.mode != "RGB":
            img = img.convert("RGB")
        clips.append(ImageClip(np.array(img)).set_duration(duration / max(random.randint(2, 5), len(images))))
    return concatenate_videoclips(clips=clips)

def merge_audio_video(audio, video):
    return video.set_audio(audio)

def get_corner_video(video_file, duration):
    FinalVideo = VideoFileClip(video_file, target_resolution=(100, 100)).subclip(0, 10).set_pos(("right", "bottom"))
    while FinalVideo.duration < duration:
        FinalVideo = concatenate_videoclips([FinalVideo, FinalVideo])
    return FinalVideo.subclip(0, duration).without_audio().set_pos(("right", "bottom"))

def add_corner_video(video1, video2):
    return CompositeVideoClip([video2, video1])

def merge_all_clips(clips):
    return concatenate_videoclips(clips=clips)


