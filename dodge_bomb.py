import os
import sys
import pygame as pg
import random
import time
import math


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
    # 半透明の黒い矩形を画面全体に描画
    sfc = pg.Surface((WIDTH, HEIGHT))
    sfc.fill((0, 0, 0))
    sfc.set_alpha(128)
    screen.blit(sfc, (0, 0))
    # "Game Over" のテキストを中央に表示
    font = pg.font.Font(None, 80)
    txt_sfc = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt_sfc.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(txt_sfc, txt_rct)
    # 泣き顔こうかとん画像を左右に表示
    sad_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)
    sad_kk_rct1 = sad_kk_img.get_rect(center=(WIDTH/2 - 200, HEIGHT/2))
    sad_kk_rct2 = sad_kk_img.get_rect(center=(WIDTH/2 + 200, HEIGHT/2))
    screen.blit(sad_kk_img, sad_kk_rct1)
    screen.blit(sad_kk_img, sad_kk_rct2)
    pg.display.update()
    time.sleep(5)

def init_bbs() -> tuple[list[pg.Surface], list[int]]:
    """
    大きさと加速度が異なる爆弾のSurfaceリストと加速度リストを作成する
    戻り値：(爆弾Surfaceリスト, 加速度リスト)
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        # 大きさの異なる円形Surfaceを作成
        bb_img = pg.Surface((20*r, 20*r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー、画像Surfaceを値とした辞書を作成する
    戻り値：こうかとん画像の辞書
    """
    # オリジナルのこうかとん画像を読み込む（左向き）
    kk_img0 = pg.image.load("fig/3.png")
    kk_img0 = pg.transform.rotozoom(kk_img0, 0, 0.9) # 0.9倍に縮小
    
    # オリジナル（左向き）とは別に、左右反転した画像（右向き）を準備
    kk_img1 = pg.transform.flip(kk_img0, True, False)

    # 全8方向の画像（Surface）を格納する辞書
    kk_imgs = {
        (0, 0):    kk_img0,                                 # 静止（左向きのまま）
        (5, 0):    kk_img1,                                 # 右（反転させた画像）
        (5, -5):   pg.transform.rotozoom(kk_img1, 45, 1.0), # 右上
        (0, -5):   pg.transform.rotozoom(kk_img1, 90, 1.0), # 上
        (-5, -5):  pg.transform.rotozoom(kk_img0, -45, 1.0),# 左上
        (-5, 0):   kk_img0,                                 # 左（元の画像）
        (-5, 5):   pg.transform.rotozoom(kk_img0, 45, 1.0), # 左下
        (0, 5):    pg.transform.rotozoom(kk_img0, 90, 1.0), # 下
        (5, 5):    pg.transform.rotozoom(kk_img1, -45, 1.0) # 右下
    }
    return kk_imgs

def calc_orientation(org_rct: pg.Rect, dst_rct: pg.Rect) -> tuple[float, float]:
    """
    orgからdstへのベクトルを正規化して返す
    引数1 org: 爆弾Rect
    引数2 dst: こうかとんRect
    戻り値: 正規化された方向ベクトル(vx, vy)
    """
    x_diff, y_diff = dst_rct.centerx - org_rct.centerx, dst_rct.centery - org_rct.centery
    norm = math.sqrt(x_diff**2 + y_diff**2)
    
    # 0除算を防ぐ
    if norm == 0:
        return 0, 0
        
    vx, vy = x_diff / norm, y_diff / norm
    return vx, vy

def main():
    # ゲーム画面の初期化
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 背景画像の読み込み
    clock = pg.time.Clock()
    tmr = 0

    # こうかとんの準備
    kk_imgs = get_kk_imgs() # こうかとん画像辞書を取得
    kk_img = kk_imgs[(0, 0)] # 初期状態（静止）の画像
    kk_rct = kk_img.get_rect(center=(300, 200))
    
    # 爆弾の準備
    bb_imgs, bb_accs = init_bbs() # 爆弾Surfaceリストと加速度リストを取得
    bb_img = bb_imgs[0] # 初期状態の爆弾画像
    bb_rct = bb_img.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    vx, vy = +5, +5 # 爆弾の初期速度（使わないが初期化）

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
        # 移動量タプルをキーにして、対応する画像に切り替える
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)  # こうかとんを移動
        yoko, tate = check_bound(kk_rct)  # 画面外判定
        if not yoko:
            kk_rct.move_ip(-sum_mv[0], 0)  # 横方向はみ出し修正
        if not tate:
            kk_rct.move_ip(0, -sum_mv[1])  # 縦方向はみ出し修正

        # 爆弾の拡大・加速と移動
        acc_index = min(tmr // 500, 9) # 500フレーム毎に1段階変化（最大インデックスは9）
        bb_img = bb_imgs[acc_index] # 爆弾画像を切り替え
        acc = bb_accs[acc_index]    # 加速度を取得
        bb_rct = bb_img.get_rect(center=bb_rct.center) # 画像サイズ変更に合わせてRectも更新
        vx, vy = calc_orientation(bb_rct, kk_rct)      # 爆弾からこうかとんへの方向ベクトル
        avx, avy = vx * acc * 5, vy * acc * 5          # 加速度をかけて速度を決定
        bb_rct.move_ip(avx, avy)                       # 爆弾を移動

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # 描画
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
