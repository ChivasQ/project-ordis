# Псевдокод ассистента
import winsound
import pyttsx3  # Стандартная говорилка Windows/Linux (ОЧЕНЬ ТУПАЯ)
# import rvc_infer  # Твой модуль RVC


def generate_ordis_laugh(text="Ha, Ha, Ha"):
    # 1. Генерируем "черновик" тупым роботом
    # Он прочитает это как "Ха. Ха. Ха." без эмоций, ровно.
    engine = pyttsx3.init()
    engine.save_to_file(text, 'temp_dumb.wav')
    engine.runAndWait()

    # # 2. Превращаем тупого робота в Ордиса
    # # RVC возьмет ритм робота, но даст тембр Ордиса
    # ordis_laugh_wav = rvc_infer.convert(
    #     input_path='temp_dumb.wav',
    #     model_path='ordis.pth',
    #     f0_method='rmvpe'  # Важно для сохранения интонации
    # )
generate_ordis_laugh()
winsound.PlaySound('temp_dumb.wav', winsound.SND_FILENAME)