import os
from PIL import Image, ImageDraw, ImageFont

def draw_title(draw, img_width, img_height, title_text, font_title, font_path, y_pos=60, title_max_w_ratio=0.9):
    # 横幅が見切れないように、画像幅の指定比率に収まるまでフォントサイズを自動調整
    font_size = 70
    max_w = int(img_width * title_max_w_ratio)
    
    current_font = font_title
    while True:
        try:
            current_font = ImageFont.truetype(font_path, font_size)
        except Exception:
            current_font = font_title
            break
            
        bbox = draw.textbbox((0, 0), title_text, font=current_font)
        w = bbox[2] - bbox[0]
        
        if w <= max_w or font_size <= 20:
            break
        font_size -= 2
        
    bbox = draw.textbbox((0, 0), title_text, font=current_font)
    w = bbox[2] - bbox[0]
    
    x = (img_width - w) // 2 - bbox[0]
    y = y_pos - bbox[1]

    text_color = (255, 255, 255, 255)
    stroke_color = (60, 60, 60, 230)
    
    draw.text(
        (x, y), 
        title_text, 
        font=current_font, 
        fill=text_color, 
        stroke_width=5, 
        stroke_fill=stroke_color
    )
    return current_font

def add_text_to_image(img_path, out_path, image_type):
    if not os.path.exists(img_path):
        print(f"Error: 画像が見つかりません - {img_path}")
        return

    img = Image.open(img_path).convert("RGBA")
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    font_paths = [
        r"C:\Windows\Fonts\meiryo.ttc",   
        r"C:\Windows\Fonts\meiryob.ttc",  
        r"C:\Windows\Fonts\msgothic.ttc", 
        r"C:\Windows\Fonts\yumin.ttf"     
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
        font_title = ImageFont.truetype(font_path, 70)
        font_subtitle = ImageFont.truetype(font_path, 35)
    except Exception as e:
        print(f"フォントの読み込みエラー: {e}")
        return

    if image_type == "exterior":
        title_text = "シックなモデルハウス見学会"
        # タイトル描画
        draw_title(draw, img.width, img.height, title_text, font_title, font_path, y_pos=60)
        
        # 詳細情報の描画（下部にバナー形式で配置）
        details = [
            "【日時】3月1日～3月20日",
            "【場所】東京都渋谷区",
            "【ターゲット】30代の子育て世帯向け",
            "【アピールポイント】W断熱 / シックな外観 / 優れた耐震性能"
        ]
        
        line_spacing = 15
        bottom_padding = 30
        
        # 画面幅の90%以内に全行が収まるように subtitle font size を調整
        subtitle_font_size = 35
        max_detail_w = int(img.width * 0.90)
        
        while True:
            try:
                current_subtitle_font = ImageFont.truetype(font_path, subtitle_font_size)
            except Exception:
                current_subtitle_font = font_subtitle
                break
                
            max_w = 0
            for line in details:
                bbox = draw.textbbox((0, 0), line, font=current_subtitle_font)
                w = bbox[2] - bbox[0]
                if w > max_w:
                    max_w = w
                    
            if max_w <= max_detail_w or subtitle_font_size <= 15:
                break
            subtitle_font_size -= 2
            
        font_subtitle = current_subtitle_font

        # 全行の高さを計算
        total_details_h = 0
        max_w = 0
        lines_info = []
        for line in details:
            bbox = draw.textbbox((0, 0), line, font=font_subtitle)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w > max_w:
                max_w = w
            lines_info.append((line, w, h, bbox[1]))
            total_details_h += h + line_spacing
        
        total_details_h -= line_spacing
        bottom_banner_h = total_details_h + bottom_padding * 2
        y_bottom_start = img.height - bottom_banner_h
        
        # 半透明の黒背景（シックなデザインに合わせる）
        draw.rectangle([0, y_bottom_start, img.width, img.height], fill=(0, 0, 0, 180))
        
        # 最も長い行の幅を基準にして左端のX座標(x_base)を決定
        x_base = (img.width - max_w) // 2
        
        y_offset = y_bottom_start + bottom_padding
        for line, w, h, y_min in lines_info:
            # 左揃えで描画
            draw.text((x_base, y_offset - y_min), line, font=font_subtitle, fill=(255, 255, 255, 255))
            y_offset += h + line_spacing

    elif image_type == "insulation":
        title_text = "W断熱の性能解説"
        draw_title(draw, img.width, img.height, title_text, font_title, font_path, y_pos=img.height - 150)
        
    elif image_type == "earthquake":
        title_text = "耐震性能の解説"
        draw_title(draw, img.width, img.height, title_text, font_title, font_path, y_pos=img.height - 150)

    final_img = Image.alpha_composite(img, overlay)
    final_img = final_img.convert("RGB")
    final_img.save(out_path)
    print(f"文字入り画像を保存しました:\n{out_path}")

if __name__ == "__main__":
    images_to_process = [
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\chic_model_house_exterior_1773024580839.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\chic_model_house_with_text.png",
            "type": "exterior"
        },
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\w_insulation_illustration_1773024597229.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\w_insulation_with_text.png",
            "type": "insulation"
        },
        {
            "in": r"C:\Users\ryuse\.gemini\antigravity\brain\a8e14284-acab-44f8-b8d1-31573388b44d\earthquake_resistance_illustration_1773024614528.png",
            "out": r"C:\Users\ryuse\Downloads\webtest\wp_automation\earthquake_resistance_with_text.png",
            "type": "earthquake"
        }
    ]

    for img_data in images_to_process:
        add_text_to_image(img_data["in"], img_data["out"], img_data["type"])
