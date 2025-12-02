# (핵심) 파이썬 로직 + Flask 서버

# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from dataclasses import dataclass, field
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'  # 세션을 위해 필요

# ==========================
# 0. 전역 설정 및 데이터
# ==========================

# 텍스트 데이터 (기존 코드 유지)
TEXT = {
    "ko": {
        "app_title": "중국인 유학생 월천이의 취업 도우미",
        "home": "홈",
        "menu_profile": "프로필 설정",
        "menu_jobs": "직무 추천",
        "menu_apply": "지원 현황",
        "menu_crawl": "채용 공고 검색",
        "save": "저장하기",
        "search": "검색하기",
        # ... 필요시 기존 텍스트 키 활용

        "welcome_prefix": "👋 안녕하세요, ",
        "welcome_suffix": "님!",
        "service_intro": "중국인 유학생을 위한 맞춤형 취업 도우미 서비스입니다."
    },
    "zh": {
        "app_title": "中国留学生月川的求职助手",
        "home": "首页",
        "menu_profile": "个人资料",
        "menu_jobs": "职位推荐",
        "menu_apply": "投递记录",
        "menu_crawl": "招聘信息查询",
        "save": "保存",
        "search": "搜索",

        "welcome_prefix": "👋 您好, ",
        "welcome_suffix": "!",
        "service_intro": "专为中国留学生打造的定制化求职助手服务。"
    }
}

# ==========================
# 1. 데이터 모델 (기존 클래스 활용)
# ==========================
@dataclass
class JobSeeker:
    name: str = "월천이"
    major_strengths: List[str] = field(default_factory=list)
    toeic: int = 0
    topik: int = 0
    korean_level: int = 3
    chinese_level: int = 5
    coding_level: int = 3
    prefer_fields: List[str] = field(default_factory=list)

    def english_score_level(self) -> int:
        if self.toeic <= 0: return 1
        if self.toeic < 600: return 2
        if self.toeic < 750: return 3
        if self.toeic < 900: return 4
        return 5

    def major_level(self) -> int:
        return 3 + min(len(self.major_strengths), 2)

@dataclass
class Application:
    company: str
    job_title: str
    company_type: str
    status: str
    is_public: bool
    toeic_cut: int
    foreigner_friendly: bool
    # UI 표시용 결과 텍스트
    analysis_result: str = "" 

# 전역 상태 (메모리 저장)
job_seeker = JobSeeker()
applications: List[Application] = []
public_institution_data: List[Dict[str, Any]] = []

# ==========================
# 2. 크롤러 로직 (기존 로직 함수화)
# ==========================
# (기존 PublicInstitutionRecruitCrawler, SaraminJobCrawler 등은 
#  코드가 길어서 핵심 로직만 간소화하여 포함하거나, 기존 코드를 그대로 두되
#  print 대신 리턴하도록 수정합니다.)

def get_saramin_jobs(keyword, pages=1, filter_friendly=False):
    # 기존 SaraminJobCrawler 로직을 간소화하여 리스트 반환
    headers = {'User-Agent': 'Mozilla/5.0'}
    jobs = []
    base_url = "https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={}&recruitPage={}&recruitSort=reg_dt"
    
    for page in range(1, pages + 1):
        try:
            resp = requests.get(base_url.format(keyword, page), headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("div.item_recruit")
            
            for item in items:
                try:
                    corp = item.select_one("strong.corp_name a").get_text(strip=True)
                    title = item.select_one("h2.job_tit a").get_text(strip=True)
                    link = "https://www.saramin.co.kr" + item.select_one("h2.job_tit a")["href"]
                    conds = [c.get_text(strip=True) for c in item.select("div.job_condition span")]
                    location = conds[0] if conds else ""
                    
                    # 간단한 유학생 친화 필터링
                    is_friendly = any(x in (title + corp).lower() for x in ["중국", "chinese", "유학생", "외국인"])
                    
                    if filter_friendly and not is_friendly:
                        continue
                        
                    jobs.append({
                        "company": corp,
                        "title": title,
                        "link": link,
                        "location": location,
                        "is_friendly": is_friendly
                    })
                except: continue
        except: pass
    return jobs

# ==========================
# 3. Flask 라우트 (UI 연결)
# ==========================

@app.context_processor
def inject_text():
    # 템플릿에서 t('key') 형태로 다국어 사용 가능하게 함
    lang = session.get('lang', 'ko')
    def t(key):
        return TEXT[lang].get(key, key)
    return dict(t=t, current_lang=lang)

@app.route('/')
def index():
    return render_template('index.html', seeker=job_seeker)

@app.route('/lang/<lang_code>')
def set_language(lang_code):
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global job_seeker
    if request.method == 'POST':
        job_seeker.name = request.form.get('name')
        job_seeker.major_strengths = [x.strip() for x in request.form.get('major_strengths').split(',')]
        job_seeker.toeic = int(request.form.get('toeic', 0))
        job_seeker.topik = int(request.form.get('topik', 0))
        job_seeker.korean_level = int(request.form.get('korean_level', 3))
        job_seeker.chinese_level = int(request.form.get('chinese_level', 5))
        job_seeker.coding_level = int(request.form.get('coding_level', 3))
        job_seeker.prefer_fields = [x.strip() for x in request.form.get('prefer_fields').split(',')]
        return redirect(url_for('index'))
    return render_template('profile.html', seeker=job_seeker)

@app.route('/jobs')
def jobs():
    # 직무 추천 로직 (기존 JOB_ROLES 활용)
    # 실제로는 기존 코드의 가중치 로직을 여기에 가져와서 계산합니다.
    # 예시 데이터로 대체합니다.
    recommended = [
        {"name": "데이터 분석", "score": 85, "match": "높음"},
        {"name": "해외영업(중국)", "score": 92, "match": "매우 높음"},
        {"name": "생산관리", "score": 70, "match": "보통"},
    ]
    # 실제 구현시: 기존 calc_job_match_score 함수 사용
    return render_template('jobs.html', jobs=recommended)

@app.route('/applications', methods=['GET', 'POST'])
def apply_list():
    if request.method == 'POST':
        app_obj = Application(
            company=request.form.get('company'),
            job_title=request.form.get('job_title'),
            company_type=request.form.get('company_type'),
            status=request.form.get('status'),
            is_public=(request.form.get('is_public') == 'on'),
            toeic_cut=int(request.form.get('toeic_cut', 0)),
            foreigner_friendly=(request.form.get('foreigner_friendly') == 'on')
        )
        # 간단한 분석 로직
        if app_obj.is_public and app_obj.toeic_cut > 0:
            if job_seeker.toeic >= app_obj.toeic_cut:
                app_obj.analysis_result = "토익 통과 가능 ✅"
            else:
                app_obj.analysis_result = "토익 점수 부족 ⚠️"
        
        applications.append(app_obj)
        return redirect(url_for('apply_list'))
    return render_template('applications.html', apps=applications)

@app.route('/crawl', methods=['GET', 'POST'])
def crawl():
    results = []
    keyword = "중국어"
    if request.method == 'POST':
        keyword = request.form.get('keyword', '중국어')
        only_friendly = (request.form.get('only_friendly') == 'on')
        results = get_saramin_jobs(keyword, pages=1, filter_friendly=only_friendly)
    return render_template('crawl.html', results=results, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)