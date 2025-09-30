import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1100, 650

DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0

    bb_img = pg.Surface((20, 20)) # 直径20のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) # 中心(10,10),半径10の赤い円を描画
    bb_img.set_colorkey((0, 0, 0)) # 黒い部分を透明にする
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5 # 横方向速度, 縦方向速度

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 


        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # 辞書のキーと値を一度にループで取り出す
        for key, mv in DELTA.items():
            if key_lst[key]: # もし、キーが押されていたら
                sum_mv[0] += mv[0] # X方向の移動量を加算
                sum_mv[1] += mv[1] # Y方向の移動量を加算
        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip(vx, vy) # 爆弾の移動

        screen.blit(bg_img, [0, 0])
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)

        pg.display.update()

        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
