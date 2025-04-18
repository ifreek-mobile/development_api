import requests
import fal_client
from openai import OpenAI
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# 必要に応じて使用する独自関数
from function.generate_book_pdf import generate_pdf
from function.generate_image import generate_single_image  # 単一生成関数
from function.generate_background_text import generate_background  # 改修後の関数
from function.generate_face_prompt import extract_face_features
from function.disco_prompts import (
    TEXT_1P_MAN, TEXT_1P_WOMAN, TEXT_2P_MAN, TEXT_2P_WOMAN,
    TEXT_3P_MAN, TEXT_3P_WOMAN, TEXT_4P_MAN, TEXT_4P_WOMAN,
    FACE_FEATURE_PROMPT, DANCE_IMAGE_PROMPT,
    FACE_TO_ADULT_PROMPT, ADULT_DJ_IMAGE_PROMPT
)

########################################
# Streamlit アプリ本体
########################################

st.set_page_config(
    page_title="子供ディスコAI絵本",
    page_icon="🎨",
    initial_sidebar_state="collapsed",
)

# タイトルと説明
st.title("こどもディスコ思い出絵本")
st.write("プロンプトを入力し、「絵本を作成する」→「PDFを生成する」の順で操作します。")


def initialize_session_state() -> None:
    """セッションステートの初期化"""
    session_vars = [
        "uploaded_image",
        "name",
        "gender",
        "illustration_images",     # イラスト4枚を格納するリスト
        "text_background_images",  # テキスト背景画像4枚を格納するリスト
        "pdf_data",
        "book_created"  # 絵本が生成済みかどうかを示すフラグ
    ]
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = None

    # 初期値を False にしておく
    if "book_created" not in st.session_state:
        st.session_state["book_created"] = False


def get_user_inputs() -> None:
    """名前・性別・子供の画像を入力してもらうUI"""
    st.write("名前・性別・子供の写真をアップしてね！")

    name = st.text_input("お名前を入力してください")
    gender = st.selectbox("性別を選んでください", ["選択してください", "男の子", "女の子"])
    uploaded_image = st.file_uploader("子供の写真をアップロード", type=["jpg", "png"])

    # このボタンは「絵本を作成する」(第1段階)
    if st.button("絵本を作成する"):
        # バリデーション
        if not name.strip():
            st.warning("名前を入力してください。")
            return
        if gender == "選択してください":
            st.warning("性別を選択してください。")
            return
        if not uploaded_image:
            st.warning("子供の写真をアップロードしてください。")
            return

        # セッションステートに保存
        st.session_state["name"] = name
        st.session_state["gender"] = gender
        st.session_state["uploaded_image"] = uploaded_image.getvalue()

        # 絵本生成
        process_submission()

        # 生成が終わったらフラグを True に
        st.session_state["book_created"] = True


def process_submission() -> None:
    """ユーザー入力後の処理: 画像生成やテキスト画像生成など"""
    st.info("絵本を作成中です...しばらくお待ちください。")

    # ======================
    # 画像生成（イラスト）
    # ======================
    # 1P: コーク登場シーン(固定画像)
    try:
        with open("images/dance.jpg", "rb") as f:
            page1_illustration = f.read()
    except Exception as e:
        st.error(f"1P画像読み込み中にエラー: {e}")
        page1_illustration = None

    # 2P: 子供のダンス姿
    try:
        child_face_prompt = extract_face_features(
            st.session_state["uploaded_image"], FACE_FEATURE_PROMPT.format(
                gender=st.session_state["gender"])
        )
        # print("child_face_prompt:", child_face_prompt)
        # print("-" * 50)
        page2_prompt = child_face_prompt + ", " + DANCE_IMAGE_PROMPT
        page2_illustration = generate_single_image(page2_prompt)
    except Exception as e:
        st.error(f"2P画像生成中にエラー: {e}")
        page2_illustration = None

    # 3P: コークがDJ体験へ案内(固定画像)
    try:
        with open("images/DJ.jpg", "rb") as f:
            page3_illustration = f.read()
    except Exception as e:
        st.error(f"3P画像読み込み中にエラー: {e}")
        page3_illustration = None

    # 4P: 子供が大人になった姿でDJ
    try:
        adult_face_prompt = extract_face_features(
            st.session_state["uploaded_image"], FACE_TO_ADULT_PROMPT.format(
                child_face_prompt=child_face_prompt)
        )
        # print("adult_face_prompt:", adult_face_prompt)
        # print("-" * 50)
        page4_prompt = adult_face_prompt + ", " + ADULT_DJ_IMAGE_PROMPT
        page4_illustration = generate_single_image(page4_prompt)
    except Exception as e:
        st.error(f"4P画像生成中にエラー: {e}")
        page4_illustration = None

    # リスト化してセッションに保存（1P~4P）
    st.session_state["illustration_images"] = [
        page1_illustration,
        page2_illustration,
        page3_illustration,
        page4_illustration
    ]

    # ======================
    # テキストページ用の背景画像4枚を生成
    # ======================
    name = st.session_state["name"]
    gender = st.session_state["gender"]

    # テキストを1P～4Pまで作成
    if gender == "男の子":
        t1 = TEXT_1P_MAN.format(name=name)
        t2 = TEXT_2P_MAN.format(name=name)
        t3 = TEXT_3P_MAN.format(name=name)
        t4 = TEXT_4P_MAN.format(name=name)
    else:
        t1 = TEXT_1P_WOMAN.format(name=name)
        t2 = TEXT_2P_WOMAN.format(name=name)
        t3 = TEXT_3P_WOMAN.format(name=name)
        t4 = TEXT_4P_WOMAN.format(name=name)

    # テキストをリスト化して generate_background に渡す
    texts = [t1, t2, t3, t4]
    text_backgrounds = generate_background(texts)  # 4枚のバイト列が返る想定

    st.session_state["text_background_images"] = text_backgrounds

    st.success("画像生成が完了しました。")

    # 生成結果をプレビュー表示（見開き）
    display_double_page_view()

    # --- ここにあった "PDFを生成する" ボタンは削除 or コメントアウト ---
    # if st.button("PDFを生成する"):
    #     generate_book_pdf()


def display_double_page_view() -> None:
    """
    1P~4P のイラスト画像とテキスト背景画像を見開き表示する
    """
    illustrations = st.session_state["illustration_images"]
    backgrounds = st.session_state["text_background_images"]

    if not illustrations or not backgrounds:
        st.warning("イラスト画像またはテキスト背景画像が準備されていません。")
        return

    if any(i is None for i in illustrations) or any(b is None for b in backgrounds):
        st.error("一部のページで画像が生成されていません。")
        return

    st.subheader("見開きプレビュー")

    # ページ番号(0~3) -> 1P~4P
    for i in range(4):
        st.write(f"### {i+1} ページの見開き")
        col1, col2 = st.columns(2)

        with col1:
            st.image(illustrations[i], caption=f"イラスト {i+1}P")

        with col2:
            st.image(backgrounds[i], caption=f"テキスト背景 {i+1}P")


def generate_book_pdf() -> None:
    """
    4枚のイラスト画像 + 4枚のテキスト背景画像 を
    generate_pdf() 関数に渡して PDF 化する想定
    """
    illustrations = st.session_state["illustration_images"]
    backgrounds = st.session_state["text_background_images"]

    if not illustrations or not backgrounds:
        st.error("PDF作成に必要な画像がありません。")
        return

    if len(illustrations) != 4 or len(backgrounds) != 4:
        st.error("イラスト4枚、テキスト背景4枚が揃っていません。")
        return

    pdf_data = generate_pdf(illustrations, backgrounds)

    if pdf_data:
        st.session_state["pdf_data"] = pdf_data
        st.success("PDFの生成が完了しました。")
        st.download_button(
            label="PDFをダウンロード",
            data=pdf_data,
            file_name="kodomo_disco_ehon.pdf",
            mime="application/pdf",
        )
    else:
        st.error("PDFの生成に失敗しました。")


def main() -> None:
    initialize_session_state()

    # --- 1) 入力フォーム＆「絵本を作成する」ボタン ---
    get_user_inputs()

    # --- 2) 絵本が生成されたら、「PDFを生成する」ボタンを表示 ---
    if st.session_state.get("book_created"):
        st.info("絵本が生成済みです。PDFを作成できます。")
        if st.button("PDFを生成する"):
            generate_book_pdf()


if __name__ == "__main__":
    main()
