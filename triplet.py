import pygame
import numpy as np
import wave
import math
import sys

# ================= LOAD WAV SAFELY =================
def load_wav(file):
    try:
        with wave.open(file, 'rb') as f:
            frames = f.readframes(-1)
            samples = np.frombuffer(frames, dtype=np.int16)

            if f.getnchannels() == 2:
                samples = samples.reshape((-1, 2)).mean(axis=1)

            return samples, f.getframerate()

    except wave.Error:
        print("❌ INVALID WAV FILE. Reconvert using FFmpeg.")
        sys.exit()

samples, sample_rate = load_wav("song.mp3")

# ================= ASCII =================
ASCII_ART = r"""
                                      ---------------
                                 -++==-----------------==-
                                ****+-----------------=+***+
                                **+=---------:..:------=+**@
                                +==-------*@@@@@@@@@@*==+**@
                             -@@@@@@@*++*@@@@@@@@@@@@@%****@
"""

# ================= PYGAME =================
pygame.init()

W, H = 1000, 700
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("ASCII MUSIC FIXED")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 10)

lines = ASCII_ART.splitlines()

chunk_size = 2048
offset = 0
t = 0

# ================= FFT =================
def fft_bands(chunk):
    fft = np.abs(np.fft.rfft(chunk))

    bass = np.mean(fft[0:20])
    mid = np.mean(fft[20:80])
    high = np.mean(fft[80:150])

    return bass, mid, high

# ================= LOOP =================
running = True

while running:
    screen.fill((5, 5, 12))

    W, H = screen.get_size()
    cx, cy = W // 2, H // 2

    chunk = samples[offset:offset + chunk_size]

    if len(chunk) < chunk_size:
        offset = 0
        continue

    offset += chunk_size

    bass, mid, high = fft_bands(chunk)

    # normalize
    bass = min(8, bass / 50000)
    mid = min(8, mid / 50000)
    high = min(8, high / 50000)

    beat = bass * 6

    char_w = 6
    line_h = 12

    for i, line in enumerate(lines):
        for j, ch in enumerate(line):

            if ch == " ":
                continue

            angle = t * 0.03 + i * 0.2 + j * 0.1

            x = cx + (j - len(line)/2) * char_w * (1 + bass * 0.2)
            y = cy + (i - len(lines)/2) * line_h * (1 + bass * 0.2)

            x += math.sin(angle) * (2 + beat)
            y += math.cos(angle) * (2 + mid)

            color = (
                int(min(255, bass * 200)),
                int(min(255, mid * 200)),
                int(min(255, high * 255))
            )

            # glow
            for ox, oy in [(1,0),(-1,0),(0,1),(0,-1)]:
                screen.blit(font.render(ch, True, (0, 40, 60)), (x+ox, y+oy))

            screen.blit(font.render(ch, True, color), (x, y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    t += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()