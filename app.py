"""Streamlit user interface for the GENEVA toolkit."""

from __future__ import annotations

from typing import List

from PIL import Image
import streamlit as st

from src import image_check, text_check

st.set_page_config(page_title="GENEVA – Generative Ethics Validator", layout="wide")
st.title("GENEVA – Generative Ethics Validator")

text_tab, image_tab = st.tabs(["Text Check", "Image Check"])

with text_tab:
    st.header("Textual Similarity & Repetition")
    st.write(
        "提供された文章と参照文の類似度をTF-IDFコサイン類似度で計測し、"
        "さらに繰り返し度合いを示すAIリピティションスコアを算出します。"
    )

    submission = st.text_area(
        "検査対象の文章",
        value="The quick brown fox jumps over the lazy dog. The quick brown fox repeats.",
        height=180,
    )
    reference_input = st.text_area(
        "参照文（空行で区切ると複数登録できます）",
        value=(
            "A fast brown fox leaps across a sleepy canine.\n\n"
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        ),
        height=180,
    )

    references: List[str] = [part.strip() for part in reference_input.split("\n\n") if part.strip()]

    if submission.strip() and references:
        try:
            analysis = text_check.analyse_submission(submission, references)
        except ValueError as err:
            st.error(str(err))
        else:
            st.subheader("解析結果")
            st.json(analysis.to_dict())
    else:
        st.info("文章と参照文を入力すると解析が行われます。")

with image_tab:
    st.header("Image pHash Similarity")
    st.write("2枚の画像をアップロードして、pHashベースの類似度を算出します。")

    col1, col2 = st.columns(2)
    with col1:
        file_a = st.file_uploader("画像A", type=["png", "jpg", "jpeg", "webp", "bmp"], key="image_a")
    with col2:
        file_b = st.file_uploader("画像B", type=["png", "jpg", "jpeg", "webp", "bmp"], key="image_b")

    if file_a and file_b:
        image_a = Image.open(file_a)
        image_b = Image.open(file_b)

        similarity = image_check.image_similarity(image_a, image_b)
        result = {
            "similarity": similarity,
            "hash_a": image_check.phash(image_a).flatten().tolist(),
            "hash_b": image_check.phash(image_b).flatten().tolist(),
        }

        st.subheader("解析結果")
        st.json(result)

        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.image(image_a, caption="画像A", use_column_width=True)
        with preview_col2:
            st.image(image_b, caption="画像B", use_column_width=True)
    else:
        st.info("両方の画像をアップロードすると類似度が表示されます。")
