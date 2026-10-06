# PySCFabSim 결과 대시보드

> 학생 프로젝트의 1차 프로토타입입니다. Dash + Plotly 기반 로컬·읽기 전용 결과 뷰어이며, PySCFabSim을 실행하지 않고 완료된 결과 파일을 읽습니다. SMT2020 원 논문 저자나 PySCFabSim 개발진의 공식 제품이 아닙니다.

## 1. 목표

PySCFabSim 시뮬레이션 **결과 파일만 읽어서** CR 기준 생산운영 성과와 설비 병목 후보를 탐색하는 로컬 Dash + Plotly 대시보드를 만든다. 시뮬레이터 실행과 시각화를 분리하고, 대시보드에서는 원본 결과 파일을 수정하지 않는다.

프로젝트 방향인 “동적 생산환경에서 기준 생산운영을 분석하고, 병목 및 납기 문제를 개선하는 생산 스케줄링 최적화” 중, 이번 첫 버전은 기준 운영 결과 분석에 한정한다.

## 2. 첫 버전 범위

### 포함

- 기본 샘플 JSON 또는 결과 폴더의 JSON을 선택하고, 탐색기에서 JSON을 직접 열어 로드
- 실행 설정 및 데이터 검증 상태 표시
- 완료 lot 수, 처리량, Cycle Time, 정시 완료율 등 전체 KPI 요약
- `Lot_1`, `HotLot_1` 등 lot 그룹별 처리량·Cycle Time·납기 성과 비교
- Tool Group별 Utilization, 가용률, PM, Breakdown, Setup, 평균 대기시간 탐색
- 파일을 읽기만 하는 로컬 대시보드; PySCFabSim을 실행하지 않음

### 첫 버전에서 제외

- 이벤트 애니메이션과 전체 작업 Gantt
- 날짜별 KPI 추이 및 시뮬레이션 중 실시간 모니터링
- 제품별 공정 Route 구조도와 Route → Tool Group 연결도
- 시뮬레이션 설정 변경, 재실행, 정책 최적화, 시나리오 간 통계 비교
- Excel 원본 또는 AutoSched `.asd` 입력 데이터 읽기

위 항목을 제외하는 이유는 현재 `baseline_30days.json`이 완료 lot 및 설비별 **최종 집계 결과**이기 때문이다. 개별 이벤트 시간, 일별 WIP, Route 단계 연결 관계는 결과 JSON에 들어 있지 않아 이 파일만으로는 복원할 수 없다.

## 3. 입력 파일

실제 실행 결과는 다음 폴더에서 선택하거나 탐색기에서 직접 열 수 있다. 팀원이 PySCFabSim이나 SMT2020 데이터를 설치하지 않아도 화면을 확인할 수 있도록 `examples/`에 30일 baseline과 90일·365일 결과 샘플을 포함한다.

```text
outputs/PySCFabSim_baseline/
├── baseline_30days.json   # 필수: lots, machines, plugins 집계
├── baseline_30days.log    # 선택: 데이터셋·Dispatcher·실행 일수·실행 로그
└── baseline_30days_summary.md  # 참고용 사람이 읽는 요약; 계산의 원천으로 사용하지 않음
```

저장소에 포함된 선택 가능한 JSON 샘플은 `examples/baseline_30days.json`, `examples/greedy_seed0_90days_SMT2020_LVHM_cr.json`, `examples/greedy_seed0_365days_SMT2020_LVHM_cr.json`이다. 30일 샘플만 `.log`와 요약 파일을 함께 제공하며, 90일·365일 샘플은 JSON 파일명에서 기간을 읽고 나머지 실행 메타데이터는 미상으로 표시할 수 있다.

JSON의 예상 구조:

```text
lots[lot_group] = {
  ACT, throughput, on_time, tardiness,
  waiting_time, processing_time, transport_time, waiting_time_batching
}
machines[tool_group] = {avail, util, pm, br, setup, waiting_time}
plugins[cost]
```

결과 폴더에서 선택한 파일은 같은 이름의 `.log`가 있으면 데이터셋·Dispatcher·실제 simulated days를 읽고, `_summary.md`가 있으면 seed를 읽는다. 탐색기에서 직접 연 JSON은 디스크에 저장하지 않고 현재 화면에서만 읽으며, sidecar `.log`·요약 파일은 자동으로 찾지 않는다. 이 경우 JSON 파일명에서 기간을 확인하고 나머지 실행 설정은 `미상`으로 표시할 수 있다. KPI 계산은 JSON 기준이다.

탐색기에서는 `.json` 파일 한 개씩 선택할 수 있으며, 3 MB 이하이고 최상위 `lots`, `machines` 항목이 객체인 PySCFabSim 결과를 지원한다. `examples/`의 세 JSON은 모두 완료 lot 및 설비별 최종 집계 결과 샘플이며, SMT2020 원본 모델 파일은 포함하지 않는다.

### 로컬에서 실행

PowerShell에서 대시보드 폴더로 이동해 전용 가상환경을 만들고 실행한다.

```powershell
# Run these commands from the cloned repository root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:8050`을 연다. 상단의 **한국어 / English** 버튼으로 화면 언어를 전환할 수 있으며, 선택은 해당 브라우저에 저장된다. 결과 폴더의 JSON은 파일 선택 메뉴에서 고르고, **탐색기에서 JSON 선택** 버튼으로 임의의 PySCFabSim 결과를 직접 열 수도 있다. 업로드한 JSON 내용은 대시보드 프로세스에서 분석하며 파일로 저장하지 않는다. 이 버전은 완료된 JSON 결과를 읽으며 화면에서 새 시뮬레이션을 시작하지 않는다.

대시보드 폴더만 별도 GitHub 저장소로 clone하면 환경변수가 없을 때 `examples/`의 샘플이 기본으로 열린다. 팀원들의 결과 JSON은 별도 폴더에 모아 아래 환경변수로 지정하거나, 탐색기에서 하나씩 열 수 있다. 샘플 외 실행 결과는 저장소에 추가하지 않는 것을 기본으로 한다.

```powershell
$env:PYSCFABSIM_RESULTS_DIR = "C:\path\to\outputs\PySCFabSim_baseline"
python app.py
```

```bash
export PYSCFABSIM_RESULTS_DIR="/path/to/outputs/PySCFabSim_baseline"
python app.py
```

로컬 결과 경로 선택 순서는 다음과 같다.

1. `PYSCFABSIM_RESULTS_DIR`에 지정한 경로
2. 기존 프로젝트의 `outputs/PySCFabSim_baseline` 폴더에 JSON이 있을 때 해당 폴더
3. 위 경로가 없거나 비어 있으면 저장소의 `examples/`

Vercel에서는 `PYSCFABSIM_RESULTS_DIR`을 지정하지 않으면 레포에 포함된 `examples/`를 사용한다. 업로드 JSON은 Vercel 서버에서 처리되며 디스크에 저장하지 않는다.

탐색기에서 직접 연 파일은 위 결과 목록을 변경하지 않는다. 결과 폴더에 JSON을 추가한 뒤에는 목록을 새로 읽도록 앱을 다시 시작한다.

## 4. 화면 구성

### 페이지 A — 운영 요약

- KPI 카드: 완료 lot 수, 평균 일일 처리량, 완료 lot 가중 평균 Cycle Time, 정시 완료율
- lot 그룹별 Throughput / Cycle Time 비교 차트
- 실행 데이터셋, Dispatcher, seed, simulated days와 입력 파일 이름
- 입력 누락·0으로 나누기·utilization 100% 초과 등 데이터 주의 배지

### 페이지 B — Lot 그룹 성과

- lot 그룹을 정규·Hot·SuperHot 및 제품 번호 기준으로 묶어 비교
- Cycle Time, 납기 준수율, 평균 지연일, 평균 대기/처리/운반시간
- 제품 유형 또는 우선순위 필터
- 작은 표본의 긴급 lot 그룹은 표본 수를 함께 표시

### 페이지 C — 설비 분석

- Utilization 상위 Tool Group 수평 막대 차트
- Utilization × 평균 Waiting Time 산점도
- Tool Group별 avail, util, pm, br, setup, waiting time 테이블
- 지표 선택과 상위 N개 필터
- utilization이 100%를 넘는 그룹에는 자동 병목 판정을 하지 않고 별도 검토 표시

## 5. 지표 정의

모든 계산에서 빈 값과 처리량 0인 그룹을 안전하게 처리한다.

| 표시명 | 계산 | JSON 단위 / 주의 |
|---|---|---|
| 완료 lot 수 | `Σ lots[*].throughput` | lot 건수 |
| 일평균 처리량 | 완료 lot 수 ÷ simulated days | 일수는 `.log` 또는 실행 메타데이터에서 확인 |
| 정시 완료율 | 유효한 `on_time`·`throughput` 그룹의 `Σ on_time ÷ Σ throughput × 100` | 완료된 lot 기준 가중 집계 |
| 가중 평균 Cycle Time | ACT와 처리량이 유효한 그룹의 `Σ(ACT × throughput) ÷ Σ throughput` | JSON의 ACT는 일 단위 그룹 평균 |
| 그룹별 정시율 | `on_time ÷ throughput × 100` | 표본 수 병기 |
| 그룹 평균 지연 | `tardiness ÷ throughput ÷ 86,400` | 초 단위 누적 지연을 완료 lot 기준 일수로 변환 |
| 평균 대기 / 처리 / 운반 | 각 누적 초 ÷ throughput ÷ 86,400 | lot 그룹 단위 평균 일수 |
| 설비 Utilization / avail / pm / br / setup | 각 JSON 비율 × 100 | 비율 값; util 100% 초과 시 경고 |
| 설비 평균 대기시간 | JSON의 `waiting_time` 표시 | 일 단위 |

## 6. 구성 및 파일 계획

```text
.
├── README.md                 # 이 구현 계획
├── app.py                    # Dash 앱 진입점, 페이지 레이아웃
├── requirements.txt          # 대시보드 전용 의존성
├── config.py                 # 기본 결과 폴더 및 앱 설정
├── assets/
│   └── style.css             # 대시보드 테마와 작은 화면 배치
├── examples/
│   ├── baseline_30days.json  # 30일 집계 샘플
│   ├── baseline_30days.log   # 30일 샘플 실행 설정 메타데이터
│   ├── baseline_30days_summary.md
│   ├── greedy_seed0_90days_SMT2020_LVHM_cr.json
│   └── greedy_seed0_365days_SMT2020_LVHM_cr.json
└── src/
    ├── result_loader.py      # JSON / 선택적 로그 로딩 및 스키마 확인
    ├── metrics.py            # 지표 변환과 단위 정규화
    ├── figures.py            # Plotly 차트 생성
    ├── i18n.py               # 한국어·영어 UI 문구
    └── layout.py             # 공통 화면과 섹션 구성
```

PySCFabSim 원본 코드와 SMT2020 원본 모델 데이터는 이 대시보드 저장소에 포함하지 않는다. `examples/`에는 화면 확인을 위한 집계 결과 JSON 세 개만 포함한다. 기본 결과 경로는 기존 프로젝트 구조를 위한 값이며, 독립 clone에서는 `PYSCFABSIM_RESULTS_DIR`로 로컬 결과 폴더를 지정한다.

## 7. 구현 구성 및 지표 해석

- `src/result_loader.py`: JSON 스키마 확인, 선택적 실행 로그와 요약 파일에서 메타데이터 읽기, 누락·잘못된 값 경고
- `src/metrics.py`: lot 그룹 및 설비 결과를 화면용 지표로 변환
- `src/figures.py`: Plotly 요약, lot 비교, 설비 순위와 Utilization-대기 산점도
- `src/layout.py` 및 `app.py`: 결과 선택기, 운영 요약·Lot 그룹 성과·설비 분석 탭, 필터와 표
- `assets/style.css`: 대시보드 테마와 반응형 배치

PySCFabSim lot 집계의 `tardiness`는 초 단위 누적값이다. 대시보드는 이를 86,400으로 나누어 일 단위로 표시한다. `mean_tardiness_days`는 모든 완료 lot 기준 평균 지연(정시 lot의 지연은 0으로 포함)이고, `late_lot_tardiness_days`는 지연 lot만의 평균 지연이다. 설비의 `avail`, `util`, `pm`, `br`, `setup`은 비율 값으로 저장되어 있어 화면에서 백분율로 환산한다. `machines[*].waiting_time`은 이미 일 단위여서 추가 변환하지 않는다.

현재 결과에서 Utilization이 100%를 조금 넘는 Tool Group이 있다. 화면은 해당 값을 붉게 표시하고 경고하지만, 자동 병목 판정에는 사용하지 않는다.

## 8. 완료 기준

- 저장소의 샘플 JSON으로 clone 직후 핵심 KPI와 실행 메타데이터가 표시된다.
- 결과 폴더 파일 선택 또는 탐색기 업로드로 호환 JSON을 불러올 수 있다.
- lot 우선순위·지표 선택으로 Lot 그룹 차트와 표가 갱신된다.
- 설비 지표·상위 N 선택으로 순위 차트가 갱신되며, 표에서 검색·정렬할 수 있다.
- JSON 필수 키가 없거나 값이 비어 있어도 원인과 파일 위치가 읽기 쉬운 오류로 표시된다.
- `baseline_30days.log`가 있으면 실행 정보가 표시되고, 없어도 JSON 기반 설비·lot 결과 화면은 동작한다.
- 시간 데이터가 없는 경우 날짜별 추이나 Route 구조를 제공하는 것처럼 표현하지 않는다.

## 9. 이후 확장 후보

1. PySCFabSim에서 일별 KPI 스냅샷을 별도 CSV로 저장해 날짜 추이 추가
2. 시뮬레이션 실행 ID, policy, seed가 있는 여러 결과의 비교 페이지
3. Route 및 Tool Group 입력 정보를 별도 데이터 소스로 연결해 공정 구조도 추가
4. 최적화 정책 결과를 기준 CR 결과와 비교하고 개선율·신뢰구간 표시
5. 선택 설비·선택 구간에 한해 축약 Gantt 보기 추가

## 참고

- 현재 기준 실행: `outputs/PySCFabSim_baseline/baseline_30days.json`
- 저장소 데모 결과: `examples/`의 30일·90일·365일 집계 JSON 샘플 (SMT2020 LV/HM 시뮬레이션 결과)
- PySCFabSim 결과 집계 원본: [simulation/stats.py](https://github.com/prosysscience/PySCFabSim-release/blob/master/simulation/stats.py)
- Dash 콜백 개념: <https://dash.plotly.com/basic-callbacks>

## 데이터·소프트웨어 출처

이 대시보드는 반도체 제조 스케줄링에 관한 학생 프로젝트 프로토타입이다. SMT2020 LV/HM 데이터를 사용한 PySCFabSim 결과를 읽으며, SMT2020 모델과 시뮬레이터의 원 저작자와 별도 프로젝트이다.

- **SMT2020 논문:** Kopp, D., Hassoun, M., Kalir, A., & Mönch, L. (2020). “SMT2020—A Semiconductor Manufacturing Testbed.” *IEEE Transactions on Semiconductor Manufacturing*, 33(4), 522–531. <https://doi.org/10.1109/TSM.2020.3001933>
- **SMT2020 공개 데이터:** P2SchedGen, [Simulation Models / SMT2020 Datasets](https://p2schedgen.fernuni-hagen.de/downloads/simulation). 이 프로젝트는 Dataset 2, LV/HM 모델을 사용한다. 데이터 원본 파일은 이 대시보드 저장소에 포함하지 않는다.
- **PySCFabSim 시뮬레이터:** [prosysscience/PySCFabSim-release](https://github.com/prosysscience/PySCFabSim-release). 시뮬레이터 결과 JSON을 입력으로 사용한다. [시뮬레이터의 MIT 라이선스](https://github.com/prosysscience/PySCFabSim-release/blob/master/LICENSE)는 해당 시뮬레이터 저장소에 적용되며, 이 대시보드 코드나 SMT2020 데이터의 라이선스를 자동으로 결정하지 않는다.

논문 PDF와 원본 데이터 파일은 저장소에 재배포하지 말고 위의 원 출처를 연결한다. 논문·데이터·시뮬레이터의 이용 및 재배포 조건은 각각 원 출처의 안내를 따른다.


