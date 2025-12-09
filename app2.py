import streamlit as st
import requests
import urllib.parse
import json
import time
import re

# =======================================================
# app.py: 고전 예술 기록 및 멸실유산 발굴 에이전트 (Free Version)
# =======================================================

# -------------------------------------------------------
# 1. AI 엔진 (Pollinations.ai - Free API)
# -------------------------------------------------------

def ask_ai_agent(prompt):
    """
    OpenAI 대신 Pollinations.ai 무료 API를 사용하여 텍스트를 생성합니다.
    """
    # 프롬프트 인코딩
    encoded_prompt = urllib.parse.quote(prompt)
    # 캐시 방지를 위해 랜덤 시드 추가 (선택사항)
    seed = int(time.time())
    api_url = f"https://text.pollinations.ai/{encoded_prompt}?seed={seed}&model=openai" 

    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: API status {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# -------------------------------------------------------
# 2. Mock Data 함수 (가상의 데이터베이스 역할)
# -------------------------------------------------------

def get_heritage_text_record(structure_name: str) -> dict:
    """
    (가상 DB) 작가나 유산의 이름으로 역사 기록 텍스트를 검색
    """
    time.sleep(1)  # 검색하는 척 딜레이
    
    # 예시 데이터
    if "홍길동" in structure_name:
        return {
            "status": "success",
            "search_term": structure_name,
            "text_record": (
                "홍길동 작가는 1920년대 초 일본에서 유학했으며, 당시 파리 화단의 추상적 경향에 영향을 받았다. "
                "1925년 귀국 후 조선미술전람회에서 '조선의 풍경'을 테마로 한 실험적인 단색화(Monochrome)를 선보였다. "
                "1930년대에는 캔버스에 마포를 사용한 물성 위주 작업에 집중했으며, 1935년 이후에는 채색화를 중단하고 "
                "완전한 추상으로 돌아섰다. 그의 작품은 당시 시대를 앞서간 것으로 평가받는다."
            )
        }
    elif "숭례문" in structure_name:
         return {
            "status": "success",
            "search_term": structure_name,
            "text_record": (
                "숭례문은 조선의 수도 한양의 남쪽 대문이다. 1398년(태조 7년)에 창건되었으며, "
                "1448년(세종 30년)에 크게 개축하였다. 1960년대 초반 대대적인 보수 공사가 있었고, "
                "2008년 화재로 소실되었으나 2013년 복구되었다."
            )
        }
    
    return {"status": "error", "text_record": f"'{structure_name}'에 대한 상세 기록을 데이터베이스에서 찾을 수 없습니다."}

# -------------------------------------------------------
# 3. Streamlit UI 및 로직
# -------------------------------------------------------

st.set_page_config(page_title="문화유산 에이전트 (Free)", page_icon="📜", layout="wide")

st.title("📜 지역 문화유산 디지털 마스터 에이전트")

# 사이드바 입력
with st.sidebar:
    st.header("문화유산 정보 입력")
    location = st.text_input("지역:", "서울 종로")
    structure_name = st.text_input("작가/유산 이름:", "홍길동 작가")
    
    viz_type = st.selectbox(
        "분석 시각화 형식:", 
        ['연표 (Timeline)', '요약 분석 (Summary)']
    )
    
    st.info("💡 팁: '홍길동' 또는 '숭례문'을 입력해보세요.")

# 메인 실행 버튼
if st.button("🔎 분석 및 시각화 실행"): 
    if structure_name:
        
        # 1단계: 내부 DB(Mock) 검색
        with st.spinner(f"🗄️ '{structure_name}'의 역사 기록을 데이터베이스에서 검색 중..."):
            db_result = get_heritage_text_record(structure_name)
        
        if db_result["status"] == "success":
            st.success("✅ 역사 기록을 찾았습니다!")
            
            # 검색된 텍스트 표시
            raw_text = db_result["text_record"]
            with st.expander("📜 원본 기록 보기", expanded=True):
                st.write(raw_text)

            # 2단계: AI에게 분석 요청
            with st.spinner("🤖 AI가 기록을 분석하고 시각화 데이터를 생성 중입니다..."):
                
                # 프롬프트 구성 (명확한 지시)
                system_prompt = f"""
                You are a historian and data analyst.
                Here is a historical text about '{structure_name}':
                "{raw_text}"
                
                Task 1: Analyze the text and provide a rich historical commentary in Korean.
                Task 2: If the visualization type is '연표 (Timeline)', extract events with years in JSON format.
                
                IMPORTANT:
                Your response must be in strict JSON format like this:
                {{
                    "analysis": "Your commentary here...",
                    "timeline_data": [
                        {{"year": "1920", "event": "Event description..."}},
                        {{"year": "1925", "event": "..."}}
                    ]
                }}
                
                Analyze based on the provided text. Output JSON only.
                """
                
                # AI 호출
                ai_response_text = ask_ai_agent(system_prompt)
                
                # 결과 처리 (JSON 파싱 시도)
                try:
                    # AI가 가끔 마크다운(```json ... ```)을 포함할 수 있으므로 제거 로직
                    json_match = re.search(r"\{.*\}", ai_response_text, re.DOTALL)
                    if json_match:
                        clean_json = json_match.group(0)
                        result_data = json.loads(clean_json)
                        
                        # 1. 분석 결과 출력
                        st.subheader("💡 AI 분석 결과")
                        st.write(result_data.get("analysis", "분석 내용 없음"))
                        
                        # 2. 시각화 데이터 출력
                        if viz_type == '연표 (Timeline)':
                            st.subheader("📊 활동 연표")
                            timeline = result_data.get("timeline_data", [])
                            if timeline:
                                st.dataframe(timeline, use_container_width=True)
                            else:
                                st.info("연표 데이터를 추출할 수 없습니다.")
                    else:
                        # JSON 파싱 실패 시 원문 출력
                        st.warning("AI 응답 형식이 JSON이 아닙니다. 원문을 표시합니다.")
                        st.write(ai_response_text)
                        
                except json.JSONDecodeError:
                    st.error("AI 응답을 처리하는 중 오류가 발생했습니다.")
                    st.text(ai_response_text)

        else:
            st.error(db_result["text_record"])
            
    else:
        st.warning("작가 또는 유산의 이름을 입력해주세요.")