import streamlit as st

st.set_page_config(page_title="カードゲームアプリ", page_icon="🃏", layout="wide")
st.title("カードゲームアプリへようこそ")
st.write("左側のメニューから遊びたいゲームを選んでください。")
st.markdown(
    "\n".join(
        [
            "利用できるゲーム:",
            "- ハイ&ロー",
            "- ブラックジャック",
        ]
    )
)
if st.button("メインメニューに戻る"):
    st.markdown("[メインメニューに戻る](https://shimonomasakiynu.github.io/streamlit-practice-shimono/1.0.1/)")
