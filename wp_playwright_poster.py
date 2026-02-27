import os
import sys
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("WordPressの管理画面にアクセスしています...")
        page.goto(f"{WP_URL}/wp-admin")
        
        # ログインフォームに入力
        print("ログインを試行しています...")
        if page.locator("input[name='log']").is_visible():
            page.fill("input[name='log']", WP_USER)
            page.fill("input[name='pwd']", WP_APP_PASS)
            page.click("input[name='wp-submit']")
            page.wait_for_load_state("networkidle")
            
        # ログイン成功確認 (ダッシュボード等に遷移したか)
        if "wp-admin" not in page.url or "wp-login.php" in page.url:
            print("エラー: ログインに失敗しました。Application PasswordはWebのログイン画面では使えない可能性があります。")
            browser.close()
            return

        print("ログインに成功しました！記事を投稿します。")
        page.goto(f"{WP_URL}/wp-admin/post-new.php")
        
        # 記事タイトルと本文を入力する処理 (ブロックエディタの操作)
        # タイトル入力
        page.locator("h1.wp-block-post-title").fill("春のモデルハウス見学会")
        
        # HTMLモードに切り替えて本文を入力
        # ここは実際の画面構造に合わせて調整が必要です
        # （ここでは一旦説明用コードに留めています）
        
        print("Playwrightでのブラウザ操作による投稿処理のモックが完了しました。")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    run()
