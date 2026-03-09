import os
from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(img_path, out_path):
    if not os.path.exists(img_path):
        print(f"Error: 画像が見つかりません - {img_path}")
        return

    # 透明な背景（矩形）を描画するためにRGBAモードに変換
    img = Image.open(img_path).convert("RGBA")
    
    # テキストと半透明の背景を描画するレイヤーを作成
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Windowsの標準的な日本語フォントを探す
    font_paths = [
        r"C:\Windows\Fonts\meiryo.ttc",   # メイリオ
        r"C:\Windows\Fonts\meiryob.ttc",  # メイリオ ボールド
        r"C:\Windows\Fonts\msgothic.ttc", # MSゴシック
        r"C:\Windows\Fonts\yumin.ttf"     # 游明朝
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    if not font_path:
        print("日本語フォントが見つかりませんでした。別のフォントパスを指定してください。")
        return

    try:
        # 画像サイズが1024x1024を想定したフォントサイズ設定
        font_title = ImageFont.truetype(font_path, 70)
        font_subtitle = ImageFont.truetype(font_path, 35)
    except Exception as e:
        print(f"フォントの読み込みエラー: {e}")
        return

    # ----- タイトルの描画設定 -----
    title_text = "海の家モデルハウス開催中"

    # 横幅が見切れないように、画像幅の90%に収まるまでフォントサイズを自動調整
    font_size = 70
    max_w = int(img.width * 0.90)
    
    while True:
        try:
            current_font = ImageFont.truetype(font_path, font_size)
        except Exception:
            current_font = font_title # フォントが読み込めない場合のフォールバック
            break
            
        bbox_title = draw.textbbox((0, 0), title_text, font=current_font)
        title_w = bbox_title[2] - bbox_title[0]
        title_h = bbox_title[3] - bbox_title[1]
        
        if title_w <= max_w or font_size <= 20: # 最小サイズを20とする
            break
        font_size -= 2
        
    font_title = current_font

    # 見切れないように、フォント特有の余白（bboxのズレ）を考慮して描画位置を計算
    x_title = (img.width - title_w) // 2 - bbox_title[0]
    
    # 完全に収まるようにY位置も余裕をもたせる
    # strokes（縁取り）の幅も考慮して見切れないY位置にする
    y_title = 60 - bbox_title[1]

    # 背景がないので、文字が読みやすいように白フチ（stroke）を追加して暗めの文字を描画
    text_color = (60, 60, 60, 255)
    stroke_color = (255, 255, 255, 230)
    
    draw.text(
        (x_title, y_title), 
        title_text, 
        font=font_title, 
        fill=text_color, 
        stroke_width=5, 
        stroke_fill=stroke_color
    )

    # 元の画像とテキストレイヤーを合成
    final_img = Image.alpha_composite(img, overlay)
    
    # 保存用にRGBに変換（PNGならRGBAのままでOKですが念のため）
    final_img = final_img.convert("RGB")
    final_img.save(out_path)
    print(f"文字入り画像を保存しました:\n{out_path}")

if __name__ == "__main__":
    # 処理する画像のリスト
    images_to_process = [
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\beach_house_model_1_1773023840462.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\beach_house_with_text_1.png"
        },
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\beach_house_model_2_1773023855787.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\beach_house_with_text_2.png"
        },
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\beach_house_model_3_1773023868638.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\beach_house_with_text_3.png"
        }
    ]

    for img_data in images_to_process:
        add_text_to_image(img_data["in"], img_data["out"])
