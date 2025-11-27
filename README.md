# -# career_coach_all_in_one.py
# ------------------------------------------------
# 월천이 취업 코치 (All-in-One 버전)
# 기능:
# 1. 진로 설문을 통한 직무 추천
# 2. 직무별 역량 갭 분석
# 3. 지원 현황 관리
# 4. 지표 기반 기대효과 확인
# 5. 외부 명언 API(Quotable) 기반 커리어/성공 관련 문구 제공
# 6. 외부 채용 API(Himalayas) 기반 채용 공고 예시 조회
# ------------------------------------------------

import datetime
import requests


# ------------------------------------------------
# 직무 및 필요 역량 데이터 (딕셔너리)
# ------------------------------------------------
JOBS = {
    "생산관리": {
        "필요역량": {
            "엑셀/데이터 처리": 4,
            "공정관리 지식": 3,
            "의사소통": 3
        }
    },
    "데이터분석": {
        "필요역량": {
            "파이썬": 4,
            "통계 기초": 3,
            "데이터 시각화": 3
        }
    },
    "품질관리": {
        "필요역량": {
            "통계적 품질관리(SPC)": 4,
            "문제 해결 능력": 3,
            "보고서 작성": 3
        }
    }
}


# ------------------------------------------------
# 1. 진로 설문: 적합 직무 추천
# ------------------------------------------------
class CareerSurvey:
    """간단 설문을 통해 적합한 직무를 추천하는 클래스"""

    def __init__(self):
        # 설문 문항 (key: 내부코드, value: 질문)
        self.questions = {
            "분석_선호": "숫자/데이터를 분석하는 것을 좋아한다",
            "현장_선호": "공장/현장을 돌아다니며 문제를 해결하는 것을 좋아한다",
            "사람_선호": "사람과 소통하고 협업하는 것을 좋아한다",
            "컴퓨터_선호": "자동화, 프로그래밍 같은 PC 작업을 좋아한다"
        }

    def run_survey(self):
        """설문 진행 후 직무별 점수 계산, TOP2 및 추천 직무 출력"""
        print("\n[진로 설문] 각 문항에 대해 1~5점으로 입력하세요.")
        scores = {}

        for key, q in self.questions.items():
            while True:
                try:
                    value = int(input(f"{q} (1~5): "))
                    if 1 <= value <= 5:
                        scores[key] = value
                        break
                    else:
                        print("1~5 사이의 정수를 입력해주세요.")
                except ValueError:
                    print("숫자를 입력해주세요.")

        # 직무별 적합도 점수 계산
        job_scores = {}
        job_scores["생산관리"] = scores["현장_선호"] * 2 + scores["분석_선호"]
        job_scores["데이터분석"] = scores["분석_선호"] * 2 + scores["컴퓨터_선호"]
        job_scores["품질관리"] = (
            scores["분석_선호"] + scores["현장_선호"] + scores["사람_선호"]
        )

        # 점수 내림차순 정렬
        sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)

        print("\n[설문 결과] 월천이에게 어울리는 직무 TOP 2")
        for i, (job, score) in enumerate(sorted_jobs[:2], start=1):
            print(f"{i}. {job} (점수: {score})")

        best_job = sorted_jobs[0][0]
        print(f"\n→ 추천 직무: {best_job}")
        return best_job


# ------------------------------------------------
# 2. 직무별 역량 갭 분석
# ------------------------------------------------
class SkillGapAnalyzer:
    """직무별 역량 부족도(갭)를 계산하는 클래스"""

    def __init__(self):
        self.last_gap_score = 0  # 최근 분석에서의 총 부족도 점수

    def select_job(self):
        """사용자로부터 직무 선택을 받아 직무명을 반환"""
        job_list = list(JOBS.keys())
        print("\n[직무 선택]")
        for idx, job in enumerate(job_list, start=1):
            print(f"{idx}. {job}")

        try:
            choice = int(input("번호를 선택하세요: "))
        except ValueError:
            print("숫자를 입력해주세요.")
            return None

        if 1 <= choice <= len(job_list):
            return job_list[choice - 1]
        else:
            print("목록에 있는 번호만 선택 가능합니다.")
            return None

    def analyze(self, job_name):
        """
        전달받은 직무명에 대해 필요 역량과 현재 역량을 비교하여
        부족도 점수를 계산하고 반환.
        """
        if job_name not in JOBS:
            print("등록되지 않은 직무입니다.")
            return 0

        required = JOBS[job_name]["필요역량"]
        total_gap = 0

        print(f"\n[{job_name}] 직무 역량 갭 분석")
        print("각 역량에 대해 현재 수준을 1~5로 입력하세요.")

        for skill, need_level in required.items():
            while True:
                try:
                    level = int(input(f"- {skill} 현재 수준 (1~5): "))
                except ValueError:
                    print("숫자를 입력해주세요.")
                    continue

                if not 1 <= level <= 5:
                    print("1~5 범위로 입력해주세요.")
                    continue

                gap = max(need_level - level, 0)
                total_gap += gap
                print(f"  필요 {need_level}, 현재 {level} → 부족도: {gap}")
                break

        self.last_gap_score = total_gap
        print(f"\n[{job_name}] 총 부족도 점수: {total_gap}")
        return total_gap


# ------------------------------------------------
# 3. 지원 현황 관리
# ------------------------------------------------
class ApplicationManager:
    """지원 정보 추가/조회/통계를 담당하는 클래스"""

    def __init__(self):
        # 예: {"회사명": "...", "직무": "...", "상태": "...", "지원일": "2025-11-21"}
        self.applications = []

    def add_application(self):
        """새 지원 정보를 입력받아 리스트에 추가"""
        print("\n[새 지원 추가]")
        company = input("회사명: ")
        job = input("지원 직무: ")
        status = input("현재 상태(서류접수/서류합격/불합격/면접대기 등): ")
        today = datetime.date.today().isoformat()

        app = {
            "회사명": company,
            "직무": job,
            "상태": status,
            "지원일": today
        }
        self.applications.append(app)
        print("지원 정보가 저장되었습니다.")

    def list_applications(self):
        """지원 리스트 출력"""
        if not self.applications:
            print("\n현재까지 저장된 지원 정보가 없습니다.")
            return

        print("\n[지원 목록]")
        for idx, app in enumerate(self.applications, start=1):
            print(
                f"{idx}. {app['회사명']} / {app['직무']} / "
                f"상태: {app['상태']} / 지원일: {app['지원일']}"
            )

    def get_statistics(self):
        """
        상태별/직무별 개수를 계산해서 딕셔너리로 반환.
        (지표 계산에 사용)
        """
        status_count = {}
        job_count = {}

        for app in self.applications:
            status = app["상태"]
            job = app["직무"]

            status_count[status] = status_count.get(status, 0) + 1
            job_count[job] = job_count.get(job, 0) + 1

        return status_count, job_count


# ------------------------------------------------
# 4. 지표/기대효과 계산
# ------------------------------------------------
class MetricsEngine:
    """지원 통계와 역량 갭을 기반으로 간단한 지표를 계산하는 클래스"""

    def calculate_success_rate(self, status_count):
        """
        상태별 개수에서 합격률을 계산.
        예시: "서류합격", "최종합격"을 합격으로 간주.
        """
        total = sum(status_count.values())
        if total == 0:
            return 0.0

        success_keys = ["서류합격", "최종합격"]
        success = 0
        for key in success_keys:
            success += status_count.get(key, 0)

        return round(success / total * 100, 1)

    def calculate_job_diversity(self, job_count):
        """
        몇 개의 서로 다른 직무에 지원했는지 계산.
        직무 다양성이 높을수록 탐색이 잘 되고 있다는 지표로 사용.
        """
        return len(job_count)

    def explain_effects(self, total_apps, success_rate, job_diversity, last_gap_score):
        """
        계산된 지표를 바탕으로 월천이가 어떤 도움을 받았는지
        콘솔에 설명해주는 함수.
        """
        print("\n[지표 기반 기대효과 설명]")
        print(f"- 총 지원 횟수: {total_apps}회")
        print(f"- 합격률(서류/최종 기준): {success_rate}%")
        print(f"- 지원한 직무의 개수: {job_diversity}개")
        print(f"- 최근 분석에서의 역량 부족도 점수: {last_gap_score}")

        print("\n[해석 예시]")
        if total_apps == 0:
            print("아직 지원이 이루어지지 않아, 먼저 지원 계획을 세울 필요가 있습니다.")
        else:
            print("지원 현황을 정리함으로써, 월천이가 실제로 얼마나 행동으로 옮겼는지 확인할 수 있습니다.")
            if success_rate > 0:
                print("일부 합격 사례가 발생하면서, 준비 방향이 어느 정도 맞게 설정되었다고 볼 수 있습니다.")
            else:
                print("아직 합격 사례는 없지만, 지원 횟수가 증가하면서 경험과 데이터가 쌓이고 있습니다.")

        if last_gap_score == 0:
            print("역량 부족도 점수가 0에 가까워, 목표 직무에 대한 준비 상태가 상당히 높다는 것을 의미합니다.")
        elif last_gap_score <= 3:
            print("부족한 역량이 일부 남아있지만, 집중적으로 보완하면 충분히 도전 가능한 수준입니다.")
        else:
            print("역량 부족도 점수가 높게 나타나므로, 부족한 역량을 우선적으로 보완하는 전략이 필요합니다.")


# ------------------------------------------------
# 5. 외부 명언 API (Quotable)
# ------------------------------------------------
class QuoteAPI:
    """
    외부 명언 API(Quotable)를 호출해서
    커리어/성공/미래 관련 문구를 가져오는 클래스.

    API 문서 예시: https://github.com/lukePeavey/quotable
    """

    BASE_URL = "https://api.quotable.io/random"

    def get_career_quote(self):
        """
        'business|success|future' 태그가 포함된 명언을 1개 가져와 문자열로 반환.
        오류 발생 시 기본 문구 반환.
        """
        params = {
            "tags": "business|success|future"
        }
        try:
            res = requests.get(self.BASE_URL, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()
            content = data.get("content", "")
            author = data.get("author", "Unknown")
            if content:
                return f"“{content}” - {author}"
            return "계획만 하는 사람보다, 작은 것부터 실행하는 사람이 결국 앞서갑니다."
        except Exception:
            return "네트워크 문제로 외부 명언을 불러오지 못했습니다. 그래도 오늘 한 걸음만 전진해 봅시다."


# ------------------------------------------------
# 6. 외부 채용 API (Himalayas)
# ------------------------------------------------
class JobAPIClient:
    """
    외부 채용 API(Himalayas)를 호출해서
    월천이에게 참고할 만한 채용 공고를 가져오는 클래스.

    참고: https://himalayas.app/jobs/api (공개 JSON API)
    """

    BASE_URL = "https://himalayas.app/jobs/api"

    def search_jobs(self, keyword: str, limit: int = 5):
        """
        keyword를 포함하는 채용 공고를 최대 limit개까지 반환.

        반환 형식 예:
        [
            {
                "title": "Product Engineer",
                "company": "Acme Corp",
                "category": "Engineering, Backend",
                "location": "Asia, Europe",
                "link": "https://...."
            },
            ...
        ]
        """
        try:
            params = {
                "limit": 20,  # API 최대 20개까지 반환
                "offset": 0
            }
            res = requests.get(self.BASE_URL, params=params, timeout=5)
            res.raise_for_status()
            jobs = res.json()  # 리스트 형태라고 가정

            keyword_lower = keyword.lower()
            filtered = []

            for job in jobs:
                title = job.get("title", "")
                excerpt = job.get("excerpt", "")
                combined_text = (title + " " + excerpt).lower()

                if keyword_lower in combined_text:
                    filtered.append({
                        "title": title,
                        "company": job.get("companyName", ""),
                        "category": ", ".join(job.get("category", [])),
                        "location": (
                            ", ".join(job.get("locationRestrictions", []))
                            if job.get("locationRestrictions") else "제한 없음"
                        ),
                        "link": job.get("applicationLink", "")
                    })

                if len(filtered) >= limit:
                    break

            return filtered

        except Exception as e:
            print("채용 API 호출 중 오류가 발생했습니다:", e)
            return []


# ------------------------------------------------
# 서브 메뉴 및 보조 함수
# ------------------------------------------------
def manage_applications_submenu(app_manager: ApplicationManager):
    """지원 현황 관리 서브 메뉴"""
    while True:
        print("\n[지원 현황 관리]")
        print("1. 새 지원 추가")
        print("2. 지원 목록 보기")
        print("0. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            app_manager.add_application()
        elif choice == "2":
            app_manager.list_applications()
        elif choice == "0":
            break
        else:
            print("잘못된 입력입니다.")


def show_metrics(app_manager: ApplicationManager, metrics: MetricsEngine, gap_analyzer: SkillGapAnalyzer):
    """지원 통계와 역량 갭을 기반으로 지표/기대효과 출력"""
    status_count, job_count = app_manager.get_statistics()
    total_apps = sum(status_count.values())
    success_rate = metrics.calculate_success_rate(status_count)
    job_diversity = metrics.calculate_job_diversity(job_count)
    last_gap_score = gap_analyzer.last_gap_score

    metrics.explain_effects(total_apps, success_rate, job_diversity, last_gap_score)


# ------------------------------------------------
# 메인 루프
# ------------------------------------------------
def main():
    survey = CareerSurvey()
    gap_analyzer = SkillGapAnalyzer()
    app_manager = ApplicationManager()
    metrics = MetricsEngine()
    quote_api = QuoteAPI()
    job_api = JobAPIClient()

    while True:
        print("\n===== 월천이 취업 코치 (All-in-One + 외부 API) =====")
        print("1. 진로 설문을 통한 직무 추천")
        print("2. 직무별 역량 갭 분석")
        print("3. 지원 현황 관리")
        print("4. 지표 기반 기대효과 확인")
        print("5. 커리어/성공 관련 명언 보기 (Quotable API)")
        print("6. 해외 채용 공고 예시 보기 (Himalayas API)")
        print("0. 종료")
        choice = input("메뉴 선택: ")

        if choice == "1":
            survey.run_survey()

        elif choice == "2":
            job = gap_analyzer.select_job()
            if job:
                gap_analyzer.analyze(job)

        elif choice == "3":
            manage_applications_submenu(app_manager)

        elif choice == "4":
            show_metrics(app_manager, metrics, gap_analyzer)

        elif choice == "5":
            quote = quote_api.get_career_quote()
            print("\n[오늘의 커리어 관련 한 줄]")
            print("👉", quote)

        elif choice == "6":
            keyword = input("검색 키워드(예: data, engineer, product 등): ")
            results = job_api.search_jobs(keyword, limit=5)
            if not results:
                print("\n검색된 채용 공고가 없습니다. 키워드를 바꿔보거나, 나중에 다시 시도해보세요.")
            else:
                print(f"\n[Himalayas 채용 공고 예시 - '{keyword}' 관련]")
                for idx, job in enumerate(results, start=1):
                    print(f"\n[{idx}] {job['title']} @ {job['company']}")
                    print(f"   분야: {job['category']}")
                    print(f"   근무 지역: {job['location']}")
                    print(f"   지원 링크: {job['link']}")

        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")


# 이 파일을 직접 실행했을 때만 main() 실행
if __name__ == "__main__":
    main()

