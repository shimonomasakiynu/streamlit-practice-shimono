import streamlit as st
st.title("High and Low Game にようこそ")

st.write("これは最小構成の Streamlitアプリです。")
st.write("Shimono0908")
#数値を入力するウィジェット
number = st.number_input("数値を入力してください", min_value=0, max_value=100, value=50, step=1)
st.write(f"入力された数値: {number}")
#ボタンを追加
if st.button("クリックしてね"):
    st.write("ボタンがクリックされました！")
    #2乗を表示
    st.write(f"{number}の2乗は{number**2}です")
