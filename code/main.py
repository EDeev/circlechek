from scripts import Movie, Frame
import os, shutil


def edit_circle(nearly):
    video_file = str(input("Напишите название видео: "))
    video_name = video_file[:-4]

    path = f"../videos/{video_name}"
    os.mkdir(path)

    path_video = path + "/" + video_file
    os.replace("../" + video_file, path_video)

    path_frames = path + f"/frames"
    os.mkdir(path_frames)

    path_background = path + f"/background"
    os.mkdir(path_background)

    print("\n1. Обработка видео.")
    video = Movie(path_video, video_name, path)
    procces = video.split_into_frames()

    if not procces:
        print("\nВозникла ошибка!")
        shutil.rmtree(path)
        return 0

    print("2. Обработка кадров.")

    var = int(input("Какой тип фона? Градиент или блюр: "))
    frames = list(sorted(os.listdir(path_frames)))

    for frame in frames:
        img = Frame(path_frames + "/" + frame, path_background + "/" + f'{frame[:-5]}-g.jpeg')
        width, height = img.size()

        if var:
            img.blur(width, height)
        else:
            r, g, b = img.medium_color()
            img.gradient(width, height, (r - nearly, g - nearly, b - nearly),
                         (r + nearly, g + nearly, b + nearly), (True, False, False))

        img.unity_image()

    print("\n3. Объединение кадров.")
    video.unity_into_video(frames)

    print("4. Очищение памяти.")
    os.replace(path + "/acs-" + video_file, "../acs-" + video_file)
    shutil.rmtree(path)

    print("5. Готово!")


edit_circle(10)
