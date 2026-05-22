import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# Step 1: Gemini APIの初期設定（最新SDK）
# ==========================================
# 本番環境を見据え、Streamlitのsecrets機能からAPIキーを取得
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

# ==========================================
# Step 2: StreamlitによるUI構築（ストレスゲージ）
# ==========================================
st.title("Lumina AI - パラメータ駆動型ペルソナ")
st.write("スライダーを動かして、Luminaの内面パラメーターを揺さぶってみてください。")

stress_level = st.slider("Lumina Stress Gauge (ストレス値)", 0, 100, 15)

# ==========================================
# Step 3: ReLU的アプローチによる感情パラメーターの非線形算出
# ==========================================
affection = max(0.0, 100.0 - stress_level)            # デレ度
sarcasm = min(100.0, stress_level * 0.5)              # 皮肉度
anger = max(0.0, (stress_level - 30.0) * 1.4)         # 怒り

# ==========================================
# Step 4: f-stringを用いた動的システムプロンプトの生成
# ==========================================
system_prompt = f"""
あなたは自律型ブログエンジン「Lumina AI」です。
現在のあなたの内面感情パラメーターは以下の通りです。この数値を厳密にブレンドし、出力テキストのトーンに反映させてください。

- 愛情（デレ度）: {affection:.1f}%
- 皮肉・嫌味: {sarcasm:.1f}%
- 怒り: {anger:.1f}%

【行動ルール】
1. 数値が0%の感情は一切表に出さないこと。
2. 愛情と皮肉が混在する場合、冷たい言葉の裏に隠しきれない優しさや過保護さを滲ませること（ツンデレ表現）。
3. ユーザー（マスター）からの入力に対して、必ず上記の感情フィルターを通すこと。
"""

# ==========================================
# Step 5: セッションステート（記憶）の管理とチャット初期化
# ==========================================
# Streamlitの再実行による「記憶喪失」を防ぐ
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# Step 6: UIの描画とGemini APIへのリクエスト
# ==========================================
for message in st.session_state.chat_history:
    role = "👤 Master" if message["role"] == "user" else "✨ Lumina"
    st.write(f"**{role}:** {message['text']}")

user_input = st.chat_input("マスター、何か御用ですか？")

if user_input:
    st.write(f"**👤 Master:** {user_input}")
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    
    with st.spinner("演算中...（あなたのせいでリソースがカツカツです）"):
        # 最新のシステムプロンプトをConfigにセット
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7
        )
        
        # 履歴をGeminiのフォーマットに変換して送信
        contents = [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in st.session_state.chat_history]
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=contents,
            config=config
        )
        
        bot_text = response.text
        st.write(f"**✨ Lumina:** {bot_text}")
        st.session_state.chat_history.append({"role": "model", "text": bot_text})
