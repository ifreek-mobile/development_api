import streamlit as st
import requests
import base64
from PIL import Image
import io

# タイトル表示
st.title("絵本イラスト&ストーリー作成")

# フォームを定義
with st.form(key="auto_generation_form"):
    # 各入力項目の配置
    company_name = st.selectbox("企業名(絵本種別)", options=["住宅展示", "思い出絵本"])
    name = st.text_input("名前 (10文字以内)", max_chars=10)
    gender_text = st.selectbox("性別", options=["男の子", "女の子"])
    child_face_image = st.file_uploader("子供の顔画像", type=["png", "jpg", "jpeg"])
    memory_type = st.text_input("思い出の種類(テーマ)")
    memory_text = st.text_area("思い出(内容)")

    # 送信ボタン
    submit_button = st.form_submit_button(label="実行")

# 送信ボタン押下時の処理
if submit_button:
    # 入力値のバリデーション
    errors = []
    if not name.strip():
        errors.append("【エラー】名前を入力してください。")
    if not child_face_image:
        errors.append("【エラー】子供の顔画像をアップロードしてください。")
    if not memory_type.strip():
        errors.append("【エラー】思い出の種類を入力してください。")
    if not memory_text.strip():
        errors.append("【エラー】思い出を入力してください。")

    # エラーがあれば表示し、処理終了
    if errors:
        for err in errors:
            st.error(err)
    else:
        # 性別の変換（男の子なら0、女の子なら1）
        gender = 0 if gender_text == "男の子" else 1

        # 画像データのエンコード
        image_bytes = child_face_image.read()  # バイトデータ取得
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # APIリクエスト用のペイロード作成
        payload = {
            "company_name": company_name,       # 企業名 (住宅展示 または 思い出絵本)
            "name": name,                       # 名前（10文字以内）
            "gender": gender,                   # 性別（int型）
            "child_face_image": encoded_image,  # エンコード済み画像データ
            "memory_type": memory_type,         # 思い出の種類
            "memory": memory_text               # 複数行の思い出テキスト
        }

        # APIのエンドポイントURL（例：ローカルの場合 "http://localhost:8000/api/auto_generation_book" などを使用）
        url = "https://ifreek-api.onrender.com/api/auto_generation_book"

        # APIにPOSTリクエストを送信（待機中はスピナー表示）
        try:
            with st.spinner("APIリクエスト中です…"):
                response = requests.post(url, json=payload)
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                # JSON形式でレスポンスを取得
                result = response.json()
                st.success("APIリクエストが正常に完了しました。")

                # レスポンスから各情報を取得（キー名は例として使用。実際のAPI仕様に合わせてください）
                child_story = result.get("child_story", "該当なし")
                adult_story = result.get("adult_story", "該当なし")
                child_illustration = result.get(
                    "child_generated_illustration", None)
                adult_illustration = result.get(
                    "adult_generated_illustration", None)

                # 結果表示
                st.markdown("### 子供のストーリー")
                st.write(child_story)
                st.markdown("### 大人のストーリー")
                st.write(adult_story)

                # child_illustration の表示（Base64の文字列をPILで読み込む）
                if child_illustration:
                    try:
                        image_data = base64.b64decode(child_illustration)
                        image = Image.open(io.BytesIO(image_data))
                        st.markdown("### 子供のイラスト")
                        st.image(image, caption="子供のイラスト")
                    except Exception as e:
                        st.error("子供のイラストの表示に失敗しました: " + str(e))

                # adult_illustration の表示（同様にBase64の場合）
                if adult_illustration:
                    try:
                        image_data = base64.b64decode(adult_illustration)
                        image = Image.open(io.BytesIO(image_data))
                        st.markdown("### 大人のイラスト")
                        st.image(image, caption="大人のイラスト")
                    except Exception as e:
                        st.error("大人のイラストの表示に失敗しました: " + str(e))
            else:
                st.error(f"APIリクエストに失敗しました。ステータスコード: {response.status_code}")
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
