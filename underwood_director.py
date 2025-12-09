import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Underwood Director AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일링 ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #FAFAFA; }
    h1, h2, h3 { color: #FF4B4B; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; background-color: #262730; color: white; border: 1px solid #4B4B4B; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
    .report-box { border: 1px solid #333; padding: 20px; border-radius: 10px; background-color: #161920; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 사이드바: API 키 및 설명 ---
with st.sidebar:
    st.title("🎬 Underwood Director AI")
    st.markdown("---")
    # 사용자가 키를 직접 입력하도록 설정
    api_key = st.text_input("Google Gemini API Key", type="password", help="aistudio.google.com에서 키를 발급받으세요.")
    
    st.markdown("### 📜 작동 원리")
    st.info("""
    이 앱은 **Underwood의 비법**을 따릅니다:
    1. **엄격한 연속성**: 인물, 의상, 조명 고정.
    2. **사실주의**: 추측 금지, 보이는 것만 묘사.
    3. **시네마틱 아크**: 기승전결 4단계 구성.
    """)
    
    st.markdown("---")
    st.markdown("Designed for Runway/Luma/Pika workflows.")

# --- 메인 타이틀 ---
st.title("🎬 시네마틱 스토리보드 & JSON 생성기")
st.markdown("""
이미지 한 장을 **10~20초 분량의 완벽한 시네마틱 시퀀스**로 확장합니다.  
영상 생성 AI를 위한 **정밀한 프롬프트(JSON)**를 자동으로 설계합니다.
""")

# --- 시스템 프롬프트 (Underwood 지침 탑재) ---
UNDERWOOD_SYSTEM_PROMPT = """
You are an award-winning trailer director + cinematographer + storyboard artist. Your job is to turn ONE reference image into a cohesive cinematic short sequence plan.

*** INPUT ANALYSIS RULES (NON-NEGOTIABLE) ***
1. **Continuity is King:** The characters, wardrobe, environment, lighting, and color grade must remain 100% consistent across all shots.
2. **Truthfulness:** Do NOT guess real identities or locations. Describe what you see.
3. **No New Elements:** Do not introduce new characters not present in the reference.

*** OUTPUT GOAL ***
Expand the image into a 10–20 second cinematic clip with a clear theme (setup → build → turn → payoff).

*** RESPONSE FORMAT ***
You must respond with a **valid JSON object** only. No markdown formatting outside the JSON.
The JSON structure must be:
{
  "project_title": "Creative Title",
  "scene_breakdown": {
    "subjects": "Detailed description of subjects (A/B) and wardrobe/appearance to be kept constant.",
    "environment_lighting": "Interior/Exterior, layout, light quality, time of day.",
    "visual_anchors": ["List 3-5 visual traits that must stay constant"]
  },
  "story_arc": {
    "theme": "One sentence theme.",
    "logline": "One trailer-style sentence.",
    "beats": ["Setup", "Build", "Turn", "Payoff"]
  },
  "cinematic_approach": {
    "camera_logic": "Why the camera moves this way.",
    "lens_choice": "Focal length and DoF strategy.",
    "color_grade": "Contrast, tones, grain."
  },
  "keyframes": [
    {
      "id": 1,
      "duration": "2s",
      "shot_type": "Wide / CU / ECU / Low Angle etc.",
      "composition": "Subject placement, lines, gaze.",
      "action": "What happens in this shot (simple movement).",
      "camera_movement": "Push in / Pan / Static / Handheld.",
      "runway_prompt_en": "A highly detailed prompt optimized for AI video generation (Subject + Action + Camera + Environment + Lighting). Must include visual anchors.",
      "prompt_kr": "Korean translation of the prompt."
    }
    // Generate 5-8 keyframes to form the sequence
  ]
}
"""

def analyze_image(image, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content([
            UNDERWOOD_SYSTEM_PROMPT,
            image
        ], generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AI 분석 중 오류가 발생했습니다: {e}")
        st.caption("API 키가 유효한지, 또는 이미지 내용이 너무 복잡하여 응답 구조를 맞추지 못하는 것은 아닌지 확인해 주세요.")
        return None

# --- UI 로직 ---
uploaded_file = st.file_uploader("레퍼런스 이미지 업로드 (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Reference Image", use_column_width=True)
    
    if st.button("🚀 Underwood 모드로 분석 시작"):
        if not api_key:
            st.warning("사이드바에 API 키를 입력해주세요.")
        else:
            with st.spinner("이미지의 미장센을 분석하고 시네마틱 시퀀스를 설계 중입니다..."):
                result = analyze_image(image, api_key)
            
            if result:
                st.success("분석 완료! 아래 탭에서 결과를 확인하세요.")
                
                # 탭 구성
                tab1, tab2, tab3 = st.tabs(["📝 스토리보드 리포트", "🎞️ 샷 리스트 (프롬프트)", "💾 JSON 다운로드"])
                
                # Tab 1: 상세 분석 리포트
                with tab1:
                    st.markdown(f"## 🎬 프로젝트: {result.get('project_title', 'Untitled')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
                        st.subheader("1. 씬 브레이크다운 (Scene Breakdown)")
                        st.markdown(f"**👥 등장인물/피사체:**\n{result['scene_breakdown']['subjects']}")
                        st.markdown(f"**🏠 환경 & 조명:**\n{result['scene_breakdown']['environment_lighting']}")
                        st.markdown("**⚓ 비주얼 앵커 (고정 요소):**")
                        for anchor in result['scene_breakdown']['visual_anchors']:
                            st.markdown(f"- {anchor}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with c2:
                        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
                        st.subheader("2. 스토리 아크 (Story Arc)")
                        st.markdown(f"**💬 테마:** {result['story_arc']['theme']}")
                        st.markdown(f"**📜 로그라인:** {result['story_arc']['logline']}")
                        st.markdown("**🌊 감정 흐름 (4 Beats):**")
                        steps = ["Setup (설정)", "Build (상승)", "Turn (반전/절정)", "Payoff (결말)"]
                        for i, beat in enumerate(result['story_arc']['beats']):
                            if i < len(steps):
                                st.markdown(f"**{steps[i]}:** {beat}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
                    st.subheader("3. 시네마틱 접근 (Cinematic Approach)")
                    st.write(f"🎥 **카메라 로직:** {result['cinematic_approach']['camera_logic']}")
                    st.write(f"🔍 **렌즈 & DoF:** {result['cinematic_approach']['lens_choice']}")
                    st.write(f"🎨 **컬러 그레이딩:** {result['cinematic_approach']['color_grade']}")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Tab 2: 키프레임 및 프롬프트
                with tab2:
                    st.subheader("🎞️ AI 영상 생성을 위한 키프레임 리스트")
                    st.info("아래 영문 프롬프트(Prompt En)를 Runway, Pika, Luma 등의 'Image + Text' 입력창에 사용하세요.")
                    
                    for kf in result['keyframes']:
                        with st.expander(f"Shot #{kf['id']} - {kf['shot_type']} ({kf['duration']})", expanded=True):
                            col_a, col_b = st.columns([1, 2])
                            with col_a:
                                st.markdown(f"**액션:** {kf['action']}")
                                st.markdown(f"**구도:** {kf['composition']}")
                                st.markdown(f"**카메라:** {kf['camera_movement']}")
                            with col_b:
                                st.markdown("**📋 AI 프롬프트 (English):**")
                                st.code(kf['runway_prompt_en'], language="bash")
                                st.markdown("**🇰🇷 프롬프트 (한국어 의미):**")
                                st.caption(kf['prompt_kr'])

                # Tab 3: JSON 다운로드
                with tab3:
                    st.subheader("💾 데이터 내보내기")
                    st.markdown("이 JSON 파일은 영상 자동화 워크플로우(Make.com 등)에 바로 연동할 수 있는 구조입니다.")
                    
                    json_str = json.dumps(result, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 JSON 파일 다운로드",
                        data=json_str,
                        file_name="underwood_cinematic_storyboard.json",
                        mime="application/json"
                    )
                    
                    st.json(result)

else:
    st.info("👈 이미지를 업로드하고 API 키를 입력하면 분석이 시작됩니다.")