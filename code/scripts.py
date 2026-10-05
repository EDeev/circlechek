import logging
import os

import numpy
from moviepy import AudioFileClip, ImageSequenceClip, VideoFileClip
from PIL import Image, ImageDraw, ImageFilter


class Movie:
    def __init__(self, video_file, video_name, path):
        self.video_file = video_file
        self.video_name = video_name
        self.path = path

        self.path_frames = self.path + "/frames"
        self.path_audio = self.path + f"/{self.video_name}-audio.mp3"
        self.has_audio = False

    def split_into_frames(self):
        try:
            video_clip = VideoFileClip(self.video_file)
        except Exception:
            logging.exception("Не удалось открыть кружочек")
            return False

        try:
            # у кружочка может не быть звуковой дорожки
            if video_clip.audio is not None:
                video_clip.audio.write_audiofile(self.path_audio, logger=None)
                self.has_audio = True

            step = 1 / 30.0 if video_clip.fps > 60.0 else 1 / video_clip.fps

            for count, current_duration in enumerate(numpy.arange(0, video_clip.duration, step), start=1):
                frame_filename = os.path.join(self.path_frames, f"frame-{count:05}.jpeg")
                video_clip.save_frame(frame_filename, current_duration)
        except Exception:
            logging.exception("Не удалось разобрать кружочек на кадры")
            return False
        finally:
            video_clip.close()

        return True

    def unity_into_video(self, frames):
        video_clip = VideoFileClip(self.video_file)
        fps = 30.0 if video_clip.fps > 60.0 else video_clip.fps
        video_clip.close()

        clip = ImageSequenceClip([self.path_frames + "/" + x for x in frames], fps=fps)
        if self.has_audio:
            audio_clip = AudioFileClip(self.path_audio)
            # звук не длиннее видео, иначе последний кадр «замирает»
            clip = clip.with_audio(audio_clip.subclipped(0, min(audio_clip.duration, clip.duration)))

        result = self.path + "/acs-" + self.video_name + ".mp4"
        clip.write_videofile(result, codec="libx264", audio_codec="aac", logger=None)
        clip.close()

        return result


class Frame:
    def __init__(self, filename, background):
        self.filename = filename
        self.background = background

    def size(self):
        with Image.open(self.filename) as image:
            return image.size

    def medium_color(self):
        with Image.open(self.filename) as img:
            pixels = numpy.asarray(img.convert("RGB"), dtype=numpy.float64)

        r, g, b = (int(c) for c in pixels.reshape(-1, 3).mean(axis=0))
        return r, g, b

    def gradient(self, width, height, start_list, stop_list, is_horizontal_list):
        def get_gradient(start, stop, width, height, is_horizontal):
            if is_horizontal:
                return numpy.tile(numpy.linspace(start, stop, width), (height, 1))
            else:
                return numpy.tile(numpy.linspace(start, stop, height), (width, 1)).T

        result = numpy.zeros((height, width, len(start_list)))
        for i, (start, stop, is_horizontal) in enumerate(zip(start_list, stop_list, is_horizontal_list)):
            result[:, :, i] = get_gradient(start, stop, width, height, is_horizontal)

        # без обрезки тёмные и светлые цвета «переворачиваются» при переводе в uint8
        Image.fromarray(numpy.uint8(numpy.clip(result, 0, 255))).save(self.background, quality=95)

    def blur(self, width, height):
        with Image.open(self.filename) as image:
            image = image.filter(ImageFilter.GaussianBlur(6))

        part_width = width // 64
        part_height = height // 64

        image = image.crop((part_width * 10, part_height * 10, part_width * 54, part_height * 54))
        image = image.resize((width, height))
        image.save(self.background, quality=95)

        image.close()

    def unity_image(self):
        im1 = Image.open(self.background)
        im2 = Image.open(self.filename)

        mask = Image.new("L", im2.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(((1, 1), (im2.size[0] - 1, im2.size[1] - 1)), fill=255)
        mask_blur = mask.filter(ImageFilter.GaussianBlur(1))

        im1.paste(im2, (0, 0), mask_blur)
        im1.save(self.filename)

        im1.close()
        im2.close()
        mask.close()


def process_frames(path_frames, path_background, mode):
    frames = sorted(os.listdir(path_frames))

    for frame in frames:
        img = Frame(path_frames + "/" + frame, path_background + "/" + f"{frame[:-5]}-g.jpeg")
        width, height = img.size()

        if mode == "blur":
            img.blur(width, height)
        else:
            r, g, b = img.medium_color(); nearly = 10
            img.gradient(width, height, (r - nearly, g - nearly, b - nearly),
                         (r + nearly, g + nearly, b + nearly), (True, False, False))

        img.unity_image()

    return frames
