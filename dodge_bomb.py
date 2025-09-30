import os
import sys
import pygame as pg
import random
import time

# 画面サイズの定義
WIDTH, HEIGHT = 1100, 650

# こうかとんの移動量（キー入力ごと）
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

# 作業ディレクトリをスクリプトの場所に変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し、真理値タプルを返す関数
    引数：こうかとんRectかばくだんRect
    戻り値：(横方向判定結果, 縦方向判定結果) ※画面内ならTrue
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示し、5秒間待機する
    引数：画面Surface
    """
    # 1. 黒い矩形を描画するための空のSurfaceを作り、黒い矩形を描画する
    sfc = pg.Surface((WIDTH, HEIGHT))
    sfc.fill((0, 0, 0)) # 黒で塗りつぶす
    # 2. 1のSurfaceの透明度を設定する
    sfc.set_alpha(128) # 透明度を128（半透明）に設定
    screen.blit(sfc, (0, 0))
    # 3. 白文字でGame Overと書かれたフォントSurfaceを作る
    font = pg.font.Font(None, 80) # フォントとサイズを指定
    txt_sfc = font.render("Game Over", True, (255, 255, 255)) # 白色の文字
    txt_rct = txt_sfc.get_rect(center=(WIDTH/2, HEIGHT/2)) # 画面中央に配置
    screen.blit(txt_sfc, txt_rct)
    # 4. こうかとん画像をロードし、こうかとんSurfaceを作り...
    sad_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0) # 例：泣き顔画像
    sad_kk_rct1 = sad_kk_img.get_rect(center=(WIDTH/2 - 200, HEIGHT/2))
    sad_kk_rct2 = sad_kk_img.get_rect(center=(WIDTH/2 + 200, HEIGHT/2))
    screen.blit(sad_kk_img, sad_kk_rct1)
    screen.blit(sad_kk_img, sad_kk_rct2)
    # 6. pg.display.update()したら, time.sleep(5)する
    pg.display.update()
    time.sleep(5)

def main():
    # ゲーム画面の初期化
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 背景画像の読み込み
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # こうかとん画像の読み込み・縮小
    kk_rct = kk_img.get_rect(center=(300, 200))  # こうかとんの初期位置
    clock = pg.time.Clock()
    tmr = 0

    # 爆弾（赤い円）の作成
    bb_img = pg.Surface((20, 20), pg.SRCALPHA)
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_rct = bb_img.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    vx, vy = +5, +5  # 爆弾の速度

    while True:
        # イベント処理（ウィンドウの×ボタンなど）
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # キー入力によるこうかとんの移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)  # こうかとんを移動
        yoko, tate = check_bound(kk_rct)  # 画面外判定
        if not yoko:
            kk_rct.move_ip(-sum_mv[0], 0)  # 横方向はみ出し修正
        if not tate:
            kk_rct.move_ip(0, -sum_mv[1])  # 縦方向はみ出し修正

        # 爆弾の移動
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1  # 横方向反転
        if not tate:
            vy *= -1  # 縦方向反転

        # こうかとんと爆弾の衝突判定
        if kk_rct.colliderect(bb_rct):
            # print("ゲームオーバー") # 確認用
            gameover(screen) # gameover関数を呼び出す
            return  # main関数から抜ける

        # 画面描画
        screen.blit(bg_img, [0, 0])
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()

        tmr += 1  # 経過時間カウント
        clock.tick(50)  # フレームレート制御

if __name__ == "__main__":
    pg.init()  # Pygame初期化
    main()     # メイン関数実行
    pg.quit()  # Pygame終了処理
    sys.exit() # プログラム終了
