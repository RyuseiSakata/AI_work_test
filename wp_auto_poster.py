import os
import sys
import json
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数から設定を取得
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

def check_env():
    """環境変数が正しく設定されているか確認します"""
    if not all([WP_URL, WP_USER, WP_APP_PASS]):
        print("エラー: .envファイルに WP_URL, WP_USER, WP_APP_PASS が設定されていません。")
        sys.exit(1)
    
    # URLの末尾のスラッシュを削除
    return WP_URL.rstrip('/')

def upload_image(wp_url, image_path):
    """画像をWordPressのメディアライブラリにアップロードし、Media IDを返します"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 画像をアップロード中: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"エラー: 画像ファイルが見つかりません - {image_path}")
        return None

    filename = os.path.basename(image_path)
    # 拡張子からコンテンツタイプを推測
    content_type = "image/jpeg"
    if filename.lower().endswith(".png"):
        content_type = "image/png"
    elif filename.lower().endswith(".webp"):
        content_type = "image/webp"

    endpoint = f"{wp_url}/wp-json/wp/v2/media"
    
    # 認証情報のエンコード
    auth_string = f"{WP_USER}:{WP_APP_PASS}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": content_type
    }

    try:
        with open(image_path, "rb") as file:
            response = requests.post(endpoint, headers=headers, data=file)
            
        if response.status_code == 201:
            media_id = response.json().get("id")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 画像アップロード成功 (ID: {media_id})")
            return media_id
        else:
            print(f"エラー: 画像アップロード失敗 (ステータスコード: {response.status_code})")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"例外エラーが発生しました (画像アップロード): {str(e)}")
        return None

def create_draft_post(wp_url, title, content_file, media_id=None):
    """指定されたタイトルと内容でWordPressに下書き記事を作成します"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 下書き記事を作成中: {title}")
    
    # HTMLコンテンツの読み込み
    html_content = ""
    try:
        with open(content_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"エラー: コンテンツファイルの読み込みに失敗しました - {str(e)}")
        sys.exit(1)

    endpoint = f"{wp_url}/wp-json/wp/v2/posts"
    
    # 認証情報のエンコード
    auth_string = f"{WP_USER}:{WP_APP_PASS}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": html_content,
        "status": "draft"  # 必ず下書きとして投稿
    }
    
    if media_id:
        payload["featured_media"] = media_id

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 201:
            post_id = response.json().get("id")
            post_link = response.json().get("link")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 下書きの作成に成功しました！")
            print(f"Post ID: {post_id}")
            print(f"確認URL: {wp_url}/wp-admin/post.php?post={post_id}&action=edit")
            return post_id
        else:
            print(f"エラー: 記事の投稿に失敗しました (ステータスコード: {response.status_code})")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"例外エラーが発生しました (記事投稿): {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python wp_auto_poster.py '<記事タイトル>' <htmlファイルパス> [画像ファイルパス]")
        print("例: python wp_auto_poster.py '新春！平屋モデルハウス見学会' article.html hero_image.jpg")
        sys.exit(1)

    # 引数の取得
    title = sys.argv[1]
    content_file = sys.argv[2]
    image_file = sys.argv[3] if len(sys.argv) > 3 else None

    # 環境変数のチェック
    wp_url = check_env()
    
    # 画像のアップロード (画像が指定されている場合)
    media_id = None
    if image_file:
        media_id = upload_image(wp_url, image_file)
        if not media_id:
            print("警告: 画像のアップロードに失敗したため、アイキャッチ画像なしで記事を作成します。")
    
    # 下書き記事の作成
    create_draft_post(wp_url, title, content_file, media_id)
