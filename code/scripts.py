from PIL import Image, ImageDraw, ImageFilter
from moviepy.editor import *
import numpy, os


class Movie:
    def __init__(self, video_file, video_name, path):
        self.video_file = video_file
        self.video_name = video_name
        self.path = path

        self.path_frames = ""

    def split_into_frames(self):
        video_clip = VideoFileClip(self.video_file)
        video_clip.audio.write_audiofile(self.path + f"/{self.video_name}-audio.mp3", verbose=False, logger=None)

        self.path_frames = self.path + "/frames"
        step = 1 / 30.0 if video_clip.fps > 60.0 else 1 / video_clip.fps

        count = 0
        for current_duration in numpy.arange(0, video_clip.duration, step):
            count += 1

            str_c = str(count)
            num = "00000"[:(len(str_c) * -1)] + str_c

            frame_filename = os.path.join(self.path_frames, f"frame-{num}.jpeg")
            try: video_clip.save_frame(frame_filename, current_duration)
            except Exception: return False

        video_clip.close()
        return True

    def unity_into_video(self, frames):
        video_clip = VideoFileClip(self.video_file)
        fps = 30.0 if video_clip.fps > 60.0 else video_clip.fps
        video_clip.close()
        os.remove(self.video_file)

        clip = ImageSequenceClip(list(map(lambda x: self.path_frames + "/" + x, frames)), fps=fps)
        clip.write_videofile(self.video_file, verbose=False, logger=None)
        clip.close()

        video_clip = VideoFileClip(self.video_file)
        audio_clip = AudioFileClip(self.path + f"/{self.video_name}-audio.mp3")

        video_clip_with_audio = video_clip.set_audio(audio_clip)
        video_clip_with_audio.write_videofile(self.path + "/acs-" + self.video_name + ".mp4", verbose=False, logger=None)

        video_clip.close()
        audio_clip.close()


class Frame:
    def __init__(self, filename, background):
        self.filename = filename
        self.background = background

    def size(self):
        image = Image.open(self.filename)
        width, height = image.size
        image.close()

        return width, height

    def medium_color(self):
        img = Image.open(self.filename)
        width, height = img.size

        pixels = img.load()
        r, g, b = [], [], []

        for y in range(width):
            for x in range(height):
                p = pixels[x, y]
                r.append(p[0])
                g.append(p[1])
                b.append(p[2])

        r = sum(r) // len(r)
        g = sum(g) // len(g)
        b = sum(b) // len(b)

        img.close()
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

        Image.fromarray(numpy.uint8(result)).save(self.background, quality=95)

    def blur(self, width, height):
        image = Image.open(self.filename)
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
