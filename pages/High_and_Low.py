import streamlit as st
import random

st.title("High and Low Game!")

# ① 初回のみ1~13の数字を生成して保存
if "first_num" not in st.session_state:
    st.session_state.first_num = random.randint(1, 13)

st.write(f"First Number: {st.session_state.first_num}")

# ② High, Lowのボタンを表示
choice = st.radio("Choose High or Low:", ("High", "Low"))

if st.button("Submit"):
    # ③ 新たに数字(second_num)を出力
    second_num = random.randint(1, 13)
    st.write(f"Second Number: {second_num}")

    # ④ High, Lowの判定を行う
    if (choice == "High" and second_num >= st.session_state.first_num) or (choice == "Low" and second_num < st.session_state.first_num):
        st.success("You Win!")
    else:
        st.error("You Lose!")
        