import re
import spacy
import nltk
import os 
import requests
import sys
sys.path.append('edictai/app')
sys.path.append('app')
from keybert import KeyBERT
import nltk
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
from rake_nltk import Rake
from moviepy.editor import *
from sklearn.metrics.pairwise import cosine_similarity
from moviepy.editor import VideoFileClip, concatenate_videoclips
import json
import time
from moviepy.editor import *
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
from datasets import load_dataset
from scraper_mustu import *
from image_search_mustu import *
from text_summarization_mustu import *
from keywords_extraction import *
from text_to_speech_mustu import *
from run_upload_video import *
from avatar import * 

def edict_video(url):

    # Web Scraping
    data = url_select(url)

    # News Authentication 
    # Put here 
    chunks = []

    # Text Summarization and Chunking
    if(url_identify(url)=="single"):
        content = data["content"]
        chunks = create_chunks(content)
    else:
        for single_data in data:
            chunks.append(single_data["headline"]+" "+single_data["subheadline"])
        print(chunks)


    image_filenames = []

    audio_filenames = []
    audios = []
    audio_durations = []

    image_durations = []
    images = []
    video_filenames = []

    did_filenames = []
    dids = []
    did_durations = []

    template = VideoFileClip('videos/template.mp4')
    video_filenames.append('videos/intro.mp4')

    # Image Search
    for i, chunk in enumerate(chunks):
        if(url_identify(url)=="single"):
            keywords = keywords_extraction(chunk)
            print(keywords)
            image_filename = google_image_search_api(keywords, i)
            image_filenames.append(image_filename)
        # else:
        #     for single_data in data: 
        #         image_filename = single_data["image_path"]
        #         image_filenames.append(image_filename)
        #         print(image_filenames)

    # Studio Did 
    # for i, chunk in enumerate(chunks):
    #     # audio_filename = large_tts(chunk, i)
    #     did_filename = create_a_video(f"did_chunk_{i}",chunk)
    #     # audio_filenames.append(audio_filename)
    #     did_filenames.append(did_filename)
    for i, chunk in enumerate(chunks):
        did_filenames.append(f"videos/did_chunk_{i}.mp4")

    for i, chunk in enumerate(chunks):

        # Audio Durations
        # audio = AudioFileClip(audio_filenames[i])
        did = VideoFileClip(did_filenames[i])
        # audio_duration = audio.duration
        did_duration = did.duration
        # audios.append(audio)
        dids.append(did)
        # audio_durations.append(audio_duration)
        did_durations.append(did_duration)

        # Image Durations
        image = ImageClip(image_filenames[i])
        image_duration = did.duration
        image_durations.append(image_duration)
        # Create the image clip and resize it to match the audio duration
        if did_duration > image_duration:
            image = image.resize(height=670,width=1140).set_duration(did_duration)
        else:
            image = image.resize(height=670,width=1140)
        images.append(image)

        video = CompositeVideoClip([image])

        overlay_position = (662, 127)
        final_clip_fin = CompositeVideoClip([template, video.set_pos(overlay_position)], size=template.size)

        sub_vid = final_clip_fin.set_duration(did_duration)
        
        # c=VideoFileClip("image_filename")

        new_chunk = chunk[:len(chunk)//2] + '\n' + chunk[len(chunk)//2:]

        FONT_FILE = ImageFont.truetype('fonts/RobotoSlab-Regular.ttf', 40)

        # 632 965 -- 1830 965 -- height: 1070 
        # img = Image.open("images/template.jpg")
        # draw = ImageDraw.Draw(img)
        # text_width, text_height = draw.textsize(new_chunk, font=FONT_FILE)
        # center_point = 1200
        # x_coordinate = center_point - (text_width/2)
        # draw.text((x_coordinate,1160), head_1, fill=FONT_COLOR, font=FONT_FILE3)

        textembed=TextClip(new_chunk,fontsize=40,color="white",font="Arial-Rounded-MT-Bold",stroke_color="black",stroke_width=1).set_position(("center",973)).set_duration(did_duration)

        # textembed=TextClip(new_chunk,fontsize=40,color="white",font=FONT_FILE,stroke_color="black",stroke_width=1).set_position((x_coordinate,970)).set_duration(audio_duration)
        final_clip=CompositeVideoClip([sub_vid,textembed])

        final_filename = f"videos/chunk_{i}.mp4"
         
        final_clip.write_videofile(final_filename, fps=24)

    for i, chunk in enumerate(chunks):
        # Load the videos
        video1 = VideoFileClip(f"videos/did_chunk_{i}.mp4")  # Replace with the filename of video1
        video2 = VideoFileClip(f"videos/chunk_{i}.mp4")  # Replace with the filename of video2

        # video2 = video2.without_audio()
        # final_video = CompositeVideoClip([video2.set_audio(None).set_pos((0, 100)), video1])
        # final_video = final_video.set_audio(video1.audio)

        # video2 = video2.without_audio()
        # video2 = video2.set_audio(video1.audio)
        # video2 = video2.set_duration(video1.duration)
        # overlay_position = (10, 50)
        # video1 = video1.set_position(overlay_position)
        # final_video = video2.set_position("center").on_top(video1)

        video2 = video2.without_audio()
        video2 = video2.set_audio(video1.audio)
        video2 = video2.set_duration(video1.duration)
        overlay_height = video1.size[1]//2
        overlay_width = video1.size[0]//2
        overlay_position = (316-overlay_width,461-overlay_height)
        final_video = CompositeVideoClip([video2.set_position("center"), video1.set_position(overlay_position)])

        output_filename = f"videos/new_chunk_{i}.mp4"
        final_video.write_videofile(output_filename, fps=24)

        video_filenames.append(output_filename)

    # create VideoFileClip objects from the clips
    video_filenames.append('videos/outro.mp4')
    clips_final = [VideoFileClip(video_filename) for video_filename in video_filenames]

    # concatenate the clips
    final_clip = concatenate_videoclips(clips_final)

    # write the final video to file
    final_clip.write_videofile("videos/news_edicted_11.mp4")
    
    youtubeLink = yt_upload_video("news_edicted_11.mp4", data["headline"], data["content"])
    print(youtubeLink)

    return("videos/news_edicted_11.mp4")

edict_video("https://www.hindustantimes.com/world-news/g7-countries-to-unveil-new-sanctions-targeting-russia-over-ukraine-war-101684445984345.html")
