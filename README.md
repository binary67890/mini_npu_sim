# Mini NPU Simulator | 3차 미션

파이썬으로 NPU의 MAC 연산을 이해하고, Cross(+)와 X 패턴을 분류하는 학습용 시뮬레이터

## 1. 프로젝트 개요

**NPU(Neural Processing Unit)**는 인공지능의 수많은 수치 연산을 효율적으로 처리하도록 설계된 프로세서입니다. 이번 미션에서는 NPU에서 중요한 **MAC(Multiply-Accumulate, 곱셈 후 누적 덧셈)**을 파이썬 이중 for문으로 구현합니다. 패턴과 필터를 숫자 배열로 표현하고, 같은 위치의 값을 곱해서 모두 더한 MAC 점수로 Cross와 X 중 어느 필터에 더 가까운지 판정합니다.

학습 목표는 ① 2차원 리스트 ② 함수·클래스 ③ 이중 반복문 ④ 사용자 입력 검증 ⑤ JSON 읽기·검증 ⑥ 실수 비교와 epsilon ⑦ 예외 처리 ⑧ 성능 측정입니다.

## 2. 개발 환경 및 실행 방법

확인된 환경은 Python 3.10.12, Windows + WSL2 Ubuntu, VS Code입니다. Python 3의 표준 라이브러리만 사용하며 NumPy·pandas 등 외부 패키지 설치는 필요 없습니다.

| 라이브러리 | 실제 역할 |
| --- | --- |
| json | data.json을 파이썬 자료형으로 읽기 |
| math | math.isfinite()로 유한한 실수 검사 |
| pathlib.Path | main.py 기준 파일 경로 찾기 |
| re | 패턴 이름 size_N_idx 형식 검사 |
| time.perf_counter | MAC 함수 실행 시간 측정 |

프로젝트 폴더에서 다음 명령어로 실행합니다.

```bash
python3 main.py
```

## 3. 주요 기능

### 전체 실행 흐름

```text
python3 main.py
      ↓
기존 MiniNPU 예제 → NPU 최종 연산 결과: 3.0
      ↓
메뉴 표시
  ├─ 1: 3×3 필터 A·B·패턴 입력 → MAC 점수 → A/B/UNDECIDED → 3×3 성능 측정
  ├─ 2: data.json 읽기 → 데이터 검증 → Cross/X 점수 → PASS/FAIL → 크기별 성능 측정
  └─ 0: 종료
      ↑
  1·2 완료 후 메뉴로 복귀
```

실행하면 다음 메뉴가 표시됩니다.

```text
1. 필터 A, 필터 B, 패턴 입력
2. data.json 분석
0. 종료
모드 선택:
```

### 3.1 사용자 입력 모드(3×3)

메뉴에서 1을 선택한 뒤 필터 A → 필터 B → 패턴 순으로 입력합니다. 각 행에 공백으로 구분된 숫자 3개를 넣습니다.

```text
필터 A (Cross)         필터 B (X)           패턴 (Cross)
0 1 0                 1 0 1                0 1 0
1 1 1                 0 1 0                1 1 1
0 1 0                 1 0 1                0 1 0
```

입력 예시

```text
모드 선택: 1
필터 A 1행: 0 1 0
필터 A 2행: 1 1 1
필터 A 3행: 0 1 0
필터 B 1행: 1 0 1
필터 B 2행: 0 1 0
필터 B 3행: 1 0 1
패턴 1행: 0 1 0
패턴 2행: 1 1 1
패턴 3행: 0 1 0
```

- 0 1처럼 숫자가 두 개뿐이면 해당 행만 다시 입력합니다.
- 0 a 1처럼 숫자로 바꿀 수 없는 값이 있으면 해당 행만 다시 입력합니다.
- float()로 변환하므로 정수·음수·실수를 입력할 수 있습니다.
- 주의: 직접 입력에서는 nan, inf 같은 특수 문자열이 float()로 허용될 수 있습니다. JSON 배열 검증과 달리 이를 별도로 차단하지 않으므로 향후 개선할 부분입니다.

### 3.2 JSON 데이터 분석 모드

메뉴에서 2를 선택하면 다음 순서로 분석합니다.

1. load_json_data()가 main.py와 같은 폴더의 JSON 파일을 읽습니다.
2. validate_json_data()가 필터·패턴 구조와 크기를 검사합니다.
3. analyze_json_data()가 expected 누락·잘못된 라벨도 확인합니다.
4. 정상 패턴에 Cross 및 X 필터를 적용해 각각 MAC 점수를 구합니다.
5. compare_scores()로 승자를 정하고 Cross, X, UNDECIDED로 변환합니다.
6. 정규화된 정답과 같으면 PASS, 다르거나 오류가 있으면 FAIL로 기록합니다.
7. 총 케이스, PASS, FAIL, 실패 사유와 크기별 성능을 출력하고 메뉴로 돌아갑니다.

### 3.3 성능 측정 및 결과 출력

모드 1은 입력한 배열과 A·B 점수 및 최종 판정을 출력하고, 고정 3×3 Cross 배열로 시간을 측정합니다. 모드 2는 케이스별 점수·판정·정답, PASS/FAIL 집계와 실패 사유를 출력하고, 5×5·13×13·25×25의 평균 시간을 측정합니다.

#### 모드별 동점 보고 방식

| 구분 | 모드 1: 직접 입력 | 모드 2: JSON 자동 분석 |
| --- | --- | --- |
| 동점 판단 | UNDECIDED | UNDECIDED |
| 정답(expected) | 사용하지 않음 | JSON의 expected를 Cross 또는 X로 정규화 |
| 동점 결과 보고 | 최종 판정: UNDECIDED 출력 | 예측 UNDECIDED, 지정된 정답과 불일치하므로 FAIL 및 사유 출력 |
| 통계 | PASS/FAIL 통계 없음 | 현재는 FAIL 합계에 포함; 동점 건수 별도 합계는 출력하지 않음 |

예시: A=0.9, B=0.8999999999999999이면 두 모드 모두 UNDECIDED입니다. 모드 1은 판정만 보여주지만, 모드 2에서 정답이 X라면 FAIL로 기록합니다. 현재 JSON 6개 중 동점으로 인한 FAIL은 3개입니다.

향후 코드 개선(미구현): 모드 2 요약에 UNDECIDED, 데이터 구조 오류, 예측 불일치 건수를 별도로 집계하여 원인별 통계를 표시할 수 있습니다.

## 4. 핵심 개념과 구현 코드

### 4.1 CPU와 NPU의 차이

**① 개념 설명**

CPU는 프로그램 실행과 같은 다양한 작업을 처리하는 범용 프로세서입니다. NPU는 인공지능 계산에서 반복되는 곱셈과 덧셈을 병렬로 처리하도록 설계된 프로세서입니다.

**② 프로젝트 적용**

이 프로젝트는 CPU에서 Python으로 MAC을 실행해 NPU에서 자주 쓰이는 계산을 연습합니다.

**③ 구현 코드**

```python
    def run(self, input_data):
        """입력 데이터를 받아 MAC -> Bias -> ReLU 순서로 연산 수행"""
        total = 0
        rows = len(input_data)
        cols = len(input_data[0])

        # 1. MAC 연산
        for i in range(rows):
            for j in range(cols):
                total += input_data[i][j] * self.weights[i][j]
```

**④ 코드 해설**

`MiniNPU.run()`은 합계를 0으로 초기화하고 행과 열을 순서대로 돌며 각 입력값과 가중치를 곱해 더합니다. 이 Python 루프에서 얻은 시간은 CPU에서의 함수 실행 시간입니다.

#### 기존 MiniNPU의 MAC → Bias → ReLU

MiniNPU 클래스는 가중치와 편향을 저장하고 run()으로 연산합니다. ReLU는 결과가 양수면 그대로, 0 이하이면 0을 반환합니다.

```text
입력         가중치
1 2          0.5 0.5
3 4          0.5 0.5

MAC  = 1×0.5 + 2×0.5 + 3×0.5 + 4×0.5 = 5.0
Bias = -2.0 → 5.0 - 2.0 = 3.0
ReLU = max(0, 3.0) = 3.0
출력 = NPU 최종 연산 결과: 3.0
```

시작 예제는 MAC 합계에 편향을 더하고 ReLU를 적용합니다. 두 분류 모드는 `calculate_mac()`이 반환한 점수를 그대로 비교합니다.

### 4.2 2차원 배열과 필터(Filter)

**① 개념 설명**

2차원 배열은 여러 행을 가진 표처럼 값을 저장합니다. Python의 중첩 리스트에서 `pattern[i][j]`는 i번째 행의 j번째 열을 가리킵니다. 필터는 패턴의 각 위치에 곱할 가중치를 담은 배열입니다.

**② 프로젝트 적용**

직접 입력은 3×3 배열을 사용하고, JSON 분석은 5×5·13×13·25×25 배열을 사용합니다. Cross 필터는 십자가 모양, X 필터는 대각선이 교차하는 모양과 입력이 얼마나 맞는지 점수로 나타냅니다.

**③ 구현 코드**

```python
        filter_a = input_3x3_matrix("필터 A")
        filter_b = input_3x3_matrix("필터 B")
        pattern = input_3x3_matrix("패턴")
```

```python
        score_a = calculate_mac(pattern, filter_a)
        score_b = calculate_mac(pattern, filter_b)
        decision = compare_scores(score_a, score_b)
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"최종 판정: {decision}")

        test_pattern = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        test_filter = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        print_mac_performance([(3, test_pattern, test_filter)])
```

**④ 코드 해설**

필터 A, 필터 B, 패턴을 순서대로 읽고, 동일한 패턴을 두 필터에 각각 전달해 점수를 비교합니다. 출력 후 고정 3×3 배열로 성능을 측정합니다.

### 4.3 MAC(Multiply-Accumulate) 연산

**① 개념 설명**

Multiply는 같은 위치의 두 값을 곱한다는 뜻이고, Accumulate는 그 곱을 지금까지의 합계에 더한다는 뜻입니다. 모든 위치를 방문하면 패턴과 필터의 MAC 점수 하나가 나옵니다.

**② 프로젝트 적용**

두 필터의 점수를 각각 구해 분류에 사용합니다. 외부 라이브러리 없이 행과 열을 도는 과정을 직접 구현해 각 곱이 합계에 반영되는 순서를 확인할 수 있습니다.

**③ 구현 코드**

```python
def calculate_mac(pattern, filter_weights):
    """같은 크기의 2차원 패턴과 필터에서 같은 위치의 곱을 모두 더합니다."""
    if len(pattern) != len(filter_weights):
        raise ValueError("패턴과 필터의 행 개수가 같아야 합니다.")

    rows = len(pattern)
    cols = len(pattern[0]) if rows else 0
    for i in range(rows):
        if len(pattern[i]) != cols or len(filter_weights[i]) != cols:
            raise ValueError(
                "패턴과 필터의 모든 행은 같은 열 개수를 가져야 합니다."
            )

    total = 0
    for i in range(rows):
        for j in range(cols):
            total += pattern[i][j] * filter_weights[i][j]
    return total
```

**④ 코드 해설**

먼저 행 개수와 각 행의 열 개수를 확인하고, 크기가 맞지 않으면 `ValueError`를 발생시킵니다. 바깥 반복문이 행을, 안쪽 반복문이 열을 방문하며 `total += ...`로 곱을 누적한 뒤 합계를 반환합니다.

#### 3×3 Cross 계산 예시

```text
입력 Cross 패턴       Cross 필터           X 필터
0 1 0                0 1 0                1 0 1
1 1 1                1 1 1                0 1 0
0 1 0                0 1 0                1 0 1
```

- Cross 점수: 0×0 + 1×1 + 0×0 + 1×1 + 1×1 + 1×1 + 0×0 + 1×1 + 0×0 = 5
- X 점수: 0×1 + 1×0 + 0×1 + 1×0 + 1×1 + 1×0 + 0×1 + 1×0 + 0×1 = 1
- 결과: Cross 필터의 점수(5)가 X 필터(1)보다 높습니다.

수식으로는 MAC = Σᵢ Σⱼ pattern[i][j] × filter_weights[i][j]입니다. 미리 준비된 필터의 가중치로 점수를 계산합니다.

### 4.4 JSON 데이터 구조와 스키마 검증

**① 개념 설명**

JSON은 데이터를 텍스트로 저장하는 형식입니다. JSON 객체와 배열은 Python에서 각각 `dict`와 `list`로 읽힙니다. 스키마 검증은 필수 키, 값의 형식, 배열 크기가 프로그램의 규칙에 맞는지 검사하는 과정입니다.

**② 프로젝트 적용**

`data.json`의 `filters`에는 크기별 `cross`와 `x` 필터가, `patterns`에는 입력 배열 `input`과 정답 `expected`가 들어 있습니다. 각 패턴과 같은 크기의 필터를 골라야 위치별로 곱할 수 있습니다.

```text
data.json
├── meta (version: "1.0", type: "json")
├── filters
│   ├── size_5  → cross, x (각각 5×5)
│   ├── size_13 → cross, x (각각 13×13)
│   └── size_25 → cross, x (각각 25×25)
└── patterns
    ├── size_5_1, size_5_2
    ├── size_13_1, size_13_2
    └── size_25_1, size_25_2
```

각 패턴은 input(N×N 숫자 배열), expected(정답 문자열) 항목을 갖습니다. size_13_2는 13×13 크기의 두 번째 패턴이라는 뜻입니다. 실제 정답은 + 또는 x로 기록되어 있습니다. 크기는 별도의 size 필드가 아니라 키에서 파악합니다.

**③ 구현 코드**

```python
        match = re.fullmatch(r"size_([1-9][0-9]*)_([1-9][0-9]*)", key)
        if match is None:
            errors.append("패턴 키는 size_N_idx 형식이어야 합니다 (N, idx는 양의 정수).")
        else:
            size = int(match.group(1))
            if size not in (5, 13, 25):
                errors.append(f"지원하지 않는 패턴 크기입니다: {size}")
            elif not isinstance(filters, dict):
                errors.append("filters가 없거나 객체(dict)가 아니므로 필터를 확인할 수 없습니다.")
            else:
                errors.extend(filter_errors[size])
            if isinstance(item, dict) and "input" in item:
                errors.extend(validate_matrix(item["input"], size, f"patterns.{key}.input"))
```

```python
        if not errors:
            size_key = key.rsplit("_", 1)[0]
            filters = data["filters"][size_key]
            score_cross = calculate_mac(item["input"], filters["cross"])
            score_x = calculate_mac(item["input"], filters["x"])
            decision = compare_scores(score_cross, score_x)
            prediction = {"A": "Cross", "B": "X", "UNDECIDED": "UNDECIDED"}[decision]
```

**④ 코드 해설**

`validate_json_data()`는 최상위 객체와 필수 키를 검사하고, 각 크기의 필터 두 개에 `validate_matrix()`를 적용합니다. 위 발췌에서 정규식으로 패턴 키를 해석한 뒤 해당 크기의 필터 오류를 패턴에 반영하고 입력 배열을 검증합니다. 배열은 행·열 개수가 맞고 값이 유한한 `int` 또는 `float`여야 합니다. 검증과 정답 확인을 통과하면 `rsplit("_", 1)`로 `size_13_2`에서 `size_13`을 얻어 필터를 선택하고 두 점수를 계산합니다.

### 4.5 라벨 정규화(normalize_label)

**① 개념 설명**

정규화는 같은 뜻의 여러 표기를 하나의 표준값으로 바꾸는 과정입니다. 표준값을 쓰면 철자나 기호 차이로 같은 분류가 다르게 비교되는 일을 피할 수 있습니다.

**② 프로젝트 적용**

`expected`의 `Cross`, `cross`, `+`는 모두 `Cross`로, `X`, `x`는 모두 `X`로 통일합니다.

**③ 구현 코드**

```python
def normalize_label(label):
    """지원하는 라벨의 앞뒤 공백을 제거하고 Cross 또는 X로 통일합니다."""
    if not isinstance(label, str):
        raise ValueError("라벨은 문자열이어야 합니다.")
    labels = {"cross": "Cross", "Cross": "Cross", "+": "Cross", "x": "X", "X": "X"}
    normalized = label.strip()
    if normalized not in labels:
        raise ValueError(f"알 수 없는 라벨입니다: {label!r}. cross, Cross, +, x, X 중 하나를 사용하세요.")
    return labels[normalized]
```

**④ 코드 해설**

먼저 문자열인지 검사하고 `strip()`으로 앞뒤 공백을 제거합니다. 정리된 문자열이 `labels` 딕셔너리에 있으면 대응하는 표준 문자열을 반환하고, 등록되지 않은 표기나 문자열 이외의 값이면 `ValueError`를 발생시킵니다. 대소문자 표기는 딕셔너리에 등록된 형태만 허용합니다.

#### 라벨 확장 아이디어

- 기존 분류의 별칭 추가: normalize_label()의 labels 딕셔너리에 새 표기를 추가하고, 공백 처리·정상 표기·잘못된 표기·문자열이 아닌 입력을 테스트합니다. 예를 들어 "plus": "Cross"를 추가하면 plus도 십자가 정답으로 해석할 수 있습니다.
- 새로운 분류 종류 추가: 정규화 사전만 바꿔서는 충분하지 않습니다. data.json에 새 필터를 정의하고, validate_json_data()의 필수 필터 검사, analyze_json_data()의 MAC 점수 계산·예측 변환·정답 비교 및 출력 구조를 두 필터 전용에서 여러 필터를 처리하는 구조로 수정해야 합니다.
- 변경 후 테스트: ① 새 표기의 정상 정규화 ② 앞뒤 공백 ③ 알 수 없는 라벨의 ValueError ④ 새 필터 누락·크기 오류 ⑤ 새 패턴의 PASS/FAIL ⑥ 기존 Cross/`X` 6개 사례의 회귀 테스트를 확인합니다.

### 4.6 부동소수점 오차와 epsilon

**① 개념 설명**

컴퓨터는 일부 십진 소수를 유한한 자릿수의 이진수로 정확히 표현할 수 없어 가까운 값으로 저장합니다. 이런 값으로 곱셈과 덧셈을 하면 원래 같거나 가까운 결과에도 미세한 차이가 생길 수 있습니다.

**② 프로젝트 적용**

두 모드는 `epsilon=1e-9`를 기본 절대 허용오차로 사용합니다. `1e-9`는 `0.000000001`이며, 그보다 작은 점수 차이로 승자를 정하는 것을 방지합니다.

**③ 구현 코드**

```python
def compare_scores(score_a, score_b, epsilon=1e-9):
    """점수 차이가 epsilon 미만이면 동점, 아니면 높은 점수의 필터를 반환합니다."""
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    return "A" if score_a > score_b else "B"
```

**④ 코드 해설**

함수는 두 점수 차이의 절댓값을 `epsilon`과 비교합니다. 실제 비교 연산자는 `<`입니다. 차이가 허용오차 미만이면 `UNDECIDED`를 즉시 반환하며, 정확히 허용오차와 같으면 마지막 줄에서 더 높은 점수의 필터를 선택합니다.

### 4.7 abs() 함수와 동점 판정

**① 개념 설명**

`abs()`는 수의 절댓값을 반환합니다. 차이에 절댓값을 취하면 어느 점수가 더 크든 두 점수 사이의 거리를 0 이상의 값으로 비교할 수 있습니다.

**② 프로젝트 적용**

`abs(score_a - score_b)`는 A와 B의 순서에 상관없이 동일한 동점 기준을 적용합니다. JSON 모드는 공통 비교 함수의 반환값을 분류 라벨로 바꿉니다.

**③ 구현 코드**

```python
            score_cross = calculate_mac(item["input"], filters["cross"])
            score_x = calculate_mac(item["input"], filters["x"])
            decision = compare_scores(score_cross, score_x)
            prediction = {"A": "Cross", "B": "X", "UNDECIDED": "UNDECIDED"}[decision]
            if prediction != expected:
                if prediction == "UNDECIDED":
                    errors.append(f"epsilon 기준 동점(UNDECIDED)으로 정답 {expected}와 일치하지 않습니다.")
```

**④ 코드 해설**

`compare_scores()`가 반환한 `A`와 `B`는 각각 `Cross`와 `X`로 변환됩니다. `UNDECIDED`는 같은 이름으로 유지되며, 정규화된 정답과 다르므로 동점 사유가 오류 목록에 추가됩니다.

#### MAC 점수의 해석과 epsilon 선택

현재 점수는 필터와 패턴의 원소별 곱을 모두 더한 값이며, 정규화된 확률이나 0~1 사이의 유사도가 아닙니다. 입력값·필터값에 따라 음수나 큰 양수도 가능하고, 현재 코드는 최소 점수 임계값을 적용하지 않습니다. 두 점수의 상대적인 차이만 비교합니다. 예를 들어 A=5, B=1이면 A를, A=0.1, B=0.2이면 B를 선택합니다(동점 범위 밖일 때).

epsilon=1e-9는 현재 데이터의 작은 부동소수점 차이를 동점 처리하기 위한 고정 절대 허용오차입니다. 모든 점수 크기에 적합하다고 검증된 값은 아닙니다. 점수의 크기 범위가 크게 바뀌면 abs(A-B) < epsilon 대신 상대 허용오차(예: abs(A-B) < max(abs_epsilon, rel_epsilon * max(abs(A), abs(B))))를 실험할 수 있습니다. 상대 허용오차는 현재 미구현이며 도입 시 기존 6개 결과와 경계값을 다시 시험해야 합니다.

### 4.8 PASS/FAIL 판정과 예외 처리

**① 개념 설명**

테스트는 예측 결과가 기대한 결과와 일치하는지 확인합니다. 예외 처리는 숫자로 바꿀 수 없는 입력이나 열 수가 맞지 않는 배열처럼 정상 계산을 막는 상황을 식별하고 대응하는 방법입니다.

**② 프로젝트 적용**

모드 2는 정규화한 `expected`와 예측이 일치하고 케이스 오류가 없으면 PASS로 기록합니다. 입력 구조, 정답 또는 예측에 문제가 있으면 FAIL과 사유를 기록합니다.

**③ 구현 코드**

```python
        if isinstance(item, dict):
            if "expected" not in item:
                errors.append("expected: 필수 키가 없습니다.")
            else:
                try:
                    expected = normalize_label(item["expected"])
                except ValueError as error:
                    errors.append(f"expected: {error}")
```

```python
            decision = compare_scores(score_cross, score_x)
            prediction = {"A": "Cross", "B": "X", "UNDECIDED": "UNDECIDED"}[decision]
            if prediction != expected:
                if prediction == "UNDECIDED":
                    errors.append(f"epsilon 기준 동점(UNDECIDED)으로 정답 {expected}와 일치하지 않습니다.")
                else:
                    errors.append(f"예측 {prediction}이 정답 {expected}와 일치하지 않습니다.")
        status = "FAIL" if errors else "PASS"
        print(f"{key} | {score_cross} | {score_x} | {prediction} | {expected} | {status}")
        if errors:
            failures[key] = errors
            for error in errors:
                print(f"  - {error}")
```

**④ 코드 해설**

정답 키가 없거나 정규화 중 `ValueError`가 발생하면 오류 목록에 메시지를 넣습니다. 구조와 정답에 오류가 없을 때만 점수를 계산하고, 예측이 정답과 다르면 사유를 추가합니다. 오류 목록으로 상태를 정해 출력한 후 다음 케이스를 처리합니다.

| 검사 위치 | 검사 항목 | 처리 방식 |
| --- | --- | --- |
| 모드 1 | 행당 숫자 개수 3개인지 | 잘못된 행 재입력 |
| 모드 1 | float() 변환 가능한지 | 문자 등 오류 안내 후 재입력 |
| JSON 로드 | 파일 없음·읽기/인코딩 오류·JSON 구문 오류 | 메시지 출력 후 메뉴 복귀 |
| JSON 전체 | filters, patterns 존재·객체 여부 | 공통 오류 기록 |
| JSON 필터 | size_5/13/25, cross/x 존재·형식 | 오류 기록 |
| JSON 패턴 | size_N_idx 형식, 배열 크기·숫자 | 해당 케이스 오류 기록 |
| JSON 정답 | expected 존재·지원 라벨 여부 | 해당 케이스 FAIL |

원인을 조사할 때 필수 키·배열 크기·정답 라벨 오류는 데이터/스키마 문제로 확인합니다. 구조가 정상인데 점수가 예상과 다르면 필터 선택, 같은 위치의 곱셈, 높은 점수의 라벨 변환 순서로 로직을 확인합니다. 점수가 거의 같으면 반올림 전 차이와 epsilon 조건을 대조해 수치 비교 문제를 확인합니다.

### 주요 함수와 클래스

프로그램을 작은 역할별로 분리했습니다. return은 값을 호출한 코드에 돌려주고, print()는 화면에 표시합니다.

| 이름 | 입력 | 하는 일 / 결과 |
| --- | --- | --- |
| calculate_mac(pattern, filter_weights) | 2차원 패턴·필터 | 위치별 곱을 누적하여 점수 반환; 행·열 불일치 시 ValueError |
| compare_scores(score_a, score_b, epsilon=1e-9) | 점수 두 개, 허용오차 | A, B, UNDECIDED 중 하나 반환 |
| normalize_label(label) | 정답 문자열 | cross, Cross, + → Cross; x, X → X |
| load_json_data(path=None) | 선택적 경로 | 기본적으로 main.py와 같은 폴더의 data.json 읽기 |
| validate_matrix(matrix, size, name) | 배열, 크기, 이름 | 행·열 개수, 숫자 형식 등 오류 메시지 리스트 반환 |
| validate_json_data(data) | JSON에서 읽은 데이터 | 공통 오류 errors와 패턴별 오류 cases 반환 |
| analyze_json_data() | 별도 인자 없음 | 파일 로드, 검증, 점수, 정답 비교, 결과 요약, 성능 측정 |
| measure_mac_performance(pattern, filter_weights, repeats=100) | 배열·반복 횟수 | 평균 MAC 호출 시간(ms) 반환 |
| print_mac_performance(benchmark_inputs, repeats=100) | 측정할 배열 목록 | 크기·N²·횟수·평균 시간 출력 |
| input_3x3_matrix(name) | 입력 안내 이름 | 숫자 3개씩 3행 입력받아 2차원 리스트 반환 |
| run_input_menu() | 별도 인자 없음 | 메뉴 반복 및 선택한 모드 실행 |
| MiniNPU(weights, bias) | 가중치, 편향 | run()에서 MAC → Bias → ReLU 계산 |

## 5. 성능 분석

### 5.1 반복 측정과 평균 실행 시간

`measure_mac_performance()`는 기본 100회 반복합니다. `repeats`는 10 이상의 정수여야 하며, 기본값은 미션의 최소 10회 조건을 충족합니다.

```python
def measure_mac_performance(pattern, filter_weights, repeats=100):
    """MAC 함수 호출만 반복 측정하여 평균 밀리초를 반환합니다."""
    if type(repeats) is not int or repeats < 10:
        raise ValueError("성능 측정 반복 횟수는 10 이상의 정수여야 합니다.")
    elapsed = 0.0
    for _ in range(repeats):
        start = perf_counter()
        calculate_mac(pattern, filter_weights)
        end = perf_counter()
        elapsed += end - start
    return elapsed / repeats * 1000
```

평균 시간(ms) = [각 호출의 경과 시간(초) 합계 ÷ 반복 횟수] × 1000
파일 읽기·배열 준비·화면 출력은 측정 구간에서 제외하지만 MAC 함수 내부의 배열 크기 확인은 포함됩니다. 반복 횟수는 10 이상의 정수여야 합니다.

각 호출의 시작과 종료 시각은 `perf_counter()`로 읽습니다. 경과 시간 합계를 반복 횟수로 나눈 다음 1,000을 곱해 초를 밀리초로 변환합니다.

### 5.2 배열 크기별 연산 횟수

| 배열 크기 | 위치별 곱셈·누적 횟수 N² (1회 호출) | 반복 | 기록된 평균 시간(ms) |
| --- | --- | --- | --- |
| 3×3 | 9 | 100 | 0.001541520 |
| 5×5 | 25 | 100 | 0.003066230 |
| 13×13 | 169 | 100 | 0.009784990 |
| 25×25 | 625 | 100 | 0.043508680 |

위 수치는 기존 README에 남긴 한 차례의 실제 측정 기록으로, 컴퓨터 상태와 실행 시점에 따라 달라집니다. 3×3은 고정 Cross 배열을 사용하고, 나머지는 크기별 첫 번째 구조 검증 정상 패턴과 Cross 필터를 사용합니다. 정답 비교에서 FAIL이더라도 구조가 정상이면 성능 측정에 사용할 수 있습니다.

JSON 분석 모드의 성능표에는 5×5·13×13·25×25가 표시됩니다. 미션에서 JSON 분석 성능표에 포함하도록 명시한 3×3 측정은 현재 직접 입력 모드에서 확인할 수 있습니다.

### 5.3 시간 복잡도 O(N²)

N×N 배열에서 N개의 행 × N개의 열 = N²개 위치를 계산하므로 MAC의 시간 복잡도는 **O(N²)**입니다. 한 변이 두 배면 계산 위치는 네 배가 됩니다. 하지만 실제 시간에는 파이썬 실행 비용, 함수 호출, 크기 검사, 운영체제 스케줄링 등이 더해져 정확히 네 배로 증가하지는 않습니다. 이 수치는 실제 NPU 하드웨어의 성능을 나타내지 않습니다.

#### 측정값과 연산 위치 수의 관계

| 배열 | 위치 수 N² | 3×3 대비 위치 수 | 3×3 대비 평균 측정 시간 |
| --- | --- | --- | --- |
| 3×3 | 9 | 1.00배 | 1.00배 |
| 5×5 | 25 | 2.78배 | 1.99배 |
| 13×13 | 169 | 18.78배 | 6.35배 |
| 25×25 | 625 | 69.44배 | 28.22배 |

배열 크기에 따른 작업량은 N²로 늘지만 짧은 함수 실행 시간에는 검증·함수 호출·타이머 비용이 포함되어 비율이 정확히 일치하지 않습니다. 위 비율은 기록된 한 번의 측정값을 이용한 비교입니다.

측정 구간: 시작 시간 기록 → calculate_mac() 호출(행·열 크기 검사 + 이중 곱셈·누적) → 종료 시간 기록. 파일 I/O는 제외합니다. 순수 곱셈·누적 루프만 따로 측정하는 기능은 현재 구현하지 않았으며 향후 비교 실험 대상입니다.

## 6. 결과 리포트

### 6.1 전체 테스트, 통과, 실패

기존 실행 기록에서 JSON 구조 검증은 정상 6개, 오류 0개, 정답 판정은 PASS 3개 / FAIL 3개였습니다. 아래 점수는 가독성을 위해 일부 반올림했으며 실제 판정은 반올림 전 점수로 수행합니다.

| 케이스 ID | Cross 점수 | X 점수 | 예측 | 정답 | 결과 |
| --- | --- | --- | --- | --- | --- |
| size_5_1 | 0.9 | 0.8999999999999999 | UNDECIDED | X | FAIL |
| size_5_2 | 8.9 | 0.1 | Cross | Cross | PASS |
| size_13_1 | 0.3 | 약 14.7 | X | X | PASS |
| size_13_2 | 7.499999999999997 | 7.5 | UNDECIDED | Cross | FAIL |
| size_25_1 | 4.9 | 4.899999999999999 | UNDECIDED | X | FAIL |
| size_25_2 | 52.9 | 0.1 | Cross | Cross | PASS |

| 구분 | 건수 | 해석 |
| --- | --- | --- |
| 전체 JSON 패턴 | 6 | 5×5·13×13·25×25 각각 2개 |
| PASS | 3 | 예측과 정답이 일치 |
| FAIL | 3 | 모두 epsilon 기준 동점으로 UNDECIDED |
| 구조 검증 오류 | 0 | 제공된 실제 데이터에서 확인된 오류 없음 |
| 동점(UNDECIDED) | 3 | 현재 코드에는 별도 집계 출력이 없으며 기존 결과를 분석해 센 값 |

### 6.2 실패 원인 분석

- size_5_1: 두 점수 차이 약 1.11×10⁻¹⁶ → epsilon 미만 → UNDECIDED ≠ X
- size_13_2: 차이 약 2.66×10⁻¹⁵ → epsilon 미만 → UNDECIDED ≠ Cross
- size_25_1: 차이 약 1.78×10⁻¹⁵ → epsilon 미만 → UNDECIDED ≠ X

- 세 케이스는 모두 반올림 전 점수 차이가 `1e-9` 미만이어서 `UNDECIDED`로 판정됐습니다.

- 라벨 정규화는 실제 데이터의 `+`와 `x`를 예측과 같은 표기인 `Cross`와 `X`로 바꿔 비교할 수 있게 했습니다.

- 이 기록에서 데이터/스키마 오류는 0건이며, 세 실패는 모두 수치 비교 정책에 따른 정답 불일치입니다.

- 로직을 점검할 때는 필터 선택이나 누적·라벨 변환이 예상대로인지 확인합니다. 이 기록은 현재 필터 점수로 세 패턴을 구별하기 어려웠음을 보여줍니다.

### 6.3 시간 복잡도 분석 및 해석

- 배열 크기가 3×3, 5×5, 13×13, 25×25로 커지면서 MAC 한 번의 위치별 곱셈은 각각 9회, 25회, 169회, 625회로 늘었습니다.

- 바깥 반복문의 N개 행마다 안쪽 반복문이 N개 열을 계산하므로 수행하는 곱셈과 누적 덧셈은 각각 N²회입니다. 이 이중 반복문이 O(N²)의 근거입니다.

- 기존 평균 실행 시간도 배열 크기와 함께 증가했습니다. 25×25는 3×3보다 계산 위치가 69.44배 많았고, 측정 시간은 28.22배였습니다.

- 실제 측정에는 행·열 검사, 함수 호출, 타이머 비용 등이 포함되므로 기록된 시간 비율은 위치 수의 비율과 달라질 수 있습니다.

추가로 확인한 항목은 3×3 Cross 점수 5/X 점수 1, A·B 승리, epsilon 동점 및 경계값, 라벨 정규화, 잘못된 사용자 입력 재시도, 필터·정답 누락과 크기 오류, 다른 작업 폴더에서 JSON 읽기, 기존 MiniNPU 결과 3.0 등입니다.

## 7. 프로젝트 파일 구조

```text
mini_npu_sim/
├── main.py    # 연산, 검증, 메뉴, 성능 측정
├── data.json  # 크기별 필터와 패턴 6개
├── README.md  # 사용법, 원리, 테스트, 발표 자료
└── .gitignore  # Python 캐시와 가상 환경 등의 Git 제외 규칙
```

## 부록. 개발 과정에서 배운 점과 개선 방향

### 배운 점

1. 함수 분리: MAC 계산, 점수 비교, JSON 검증, 성능 측정을 역할별로 나누면 이해·테스트·수정이 쉬워집니다.
2. 입력 검증: 계산 전에 배열 크기와 자료형을 검사해야 오류 원인을 파악할 수 있습니다.
3. 실수 오차: 부동소수점의 작은 차이를 고려해 epsilon 기준을 적용했습니다.
4. 검증과 분류는 별개: 구조가 올바른 데이터도 예측이 정답과 다르면 FAIL입니다.
5. 성능과 복잡도: O(N²)는 계산량의 증가 경향이며 실제 시간은 환경에 따라 달라집니다.
6. 결과 분석: FAIL이 나왔을 때 코드를 무조건 바꾸기보다 원인을 확인해야 합니다.

### 현재 한계와 향후 개선 아이디어

| 현재 한계 | 향후 개선 아이디어 (아직 구현하지 않음) |
| --- | --- |
| 실제 NPU 칩이 아닌 CPU 기반 시뮬레이터 | 하드웨어와 병렬 처리 방식 추가 학습 |
| 두 필터 점수가 같으면 분류 불가 | 필터 구성 및 판정 기준 비교 실험 |
| 직접 입력은 3×3만 지원 | 다양한 크기의 사용자 입력 지원 |
| 직접 입력의 nan, inf 미차단 | JSON 검증처럼 유한한 숫자만 허용 |
| 성능 측정 환경에 따라 값 변동 | 반복 횟수·측정 방법을 바꿔 비교 |
| 기본 이중 반복문만 사용 | 1차원 펼치기(flatten) 방식과 성능 비교 |

### 대규모 패턴의 병목과 최적화 우선순위

현재 확인된 사실: calculate_mac()은 N×N 배열의 N²개 위치를 방문하므로 계산량이 O(N²)입니다. Python 중첩 리스트는 행별 객체를 따라 접근하므로 반복문·인덱싱·메모리 접근의 비용이 발생할 수 있습니다. JSON의 큰 배열은 파일 읽기와 파싱 과정에서 메모리 사용량도 증가시킵니다. 다만 어느 부분이 가장 느린지는 아직 프로파일링하지 않았습니다.

| 우선순위 | 병목 후보 | 확인 방법 | 개선 아이디어(미구현) |
| --- | --- | --- | --- |
| 1 | 이중 반복문의 Python 실행 비용 | 크기별 perf_counter() 측정, 반복 실행 | 불필요한 인덱싱·반복문 작업 줄이기 |
| 2 | 행렬의 메모리 접근 | 같은 데이터로 중첩 리스트와 1차원 배열 비교 | 1차원 평탄화(flatten) 방식 실험 |
| 3 | 행·열 크기 검증 비용 | 검증 포함 함수와 사전 검증 후 순수 루프를 각각 측정 | 안전한 검증 단계와 계산 단계 분리 검토 |
| 4 | 대용량 JSON 읽기·메모리 | 로드 시간과 메모리 사용량을 계산 시간과 별도로 측정 | 데이터 로드 방식·보관 구조 개선 |

CPU와 실제 NPU의 차이: 이 프로그램의 Python 루프는 CPU에서 순차 실행됩니다. 실제 NPU는 많은 MAC을 병렬 수행하도록 설계되지만, 병렬 연산량이 커져도 메모리 대역폭과 데이터 이동이 성능을 제한할 수 있습니다. CPU 시뮬레이터의 루프 시간은 실제 NPU의 연산 처리량이나 메모리 대역폭을 측정한 결과가 아닙니다.

검증 원칙: 최적화 전후에 MAC 결과가 같은지 테스트하고, 동일한 데이터·반복 횟수·측정 구간으로 비교합니다. 개선 효과가 확인되지 않으면 최적화했다고 주장하지 않습니다.

이번 프로젝트의 핵심 배움은 프로그램이 실행되는 것만큼 계산 원리와 결과의 이유를 설명하는 일이 중요하다는 점입니다.

## 부록. 발표 자료

### 3~5분 발표 원고

① 프로젝트 소개

안녕하세요. 이번 3차 미션에서 구현한 프로젝트는 Mini NPU Simulator입니다. NPU는 인공지능 연산을 효율적으로 처리하도록 설계된 프로세서입니다. 저는 NPU의 핵심 연산인 MAC을 파이썬으로 구현했습니다. MAC은 같은 위치의 두 숫자를 곱하고 그 결과를 계속 더하는 계산입니다.

② 핵심 계산 원리

입력 패턴과 필터를 2차원 숫자 배열로 표현했습니다. 예를 들어 3×3 십자가 패턴을 십자가 필터와 비교하면 MAC 점수는 5이고, X 필터와 비교하면 1입니다. 그래서 십자가 필터의 점수가 더 높다고 판단할 수 있습니다. 이 계산은 파이썬 이중 for문으로 구현했습니다.

③ 주요 기능

프로그램에는 두 가지 모드가 있습니다. 모드 1은 사용자가 3×3 필터 두 개와 패턴을 직접 입력해 점수를 비교합니다. 모드 2는 data.json에 저장된 5×5, 13×13, 25×25 패턴을 자동으로 분석하고 정답과 비교하여 PASS 또는 FAIL을 출력합니다. 입력과 JSON 구조를 검사하고 실행 시간도 측정합니다.

④ 실제 결과와 FAIL 원인

JSON의 6개 패턴을 분석한 결과 PASS 3개, FAIL 3개였습니다. 세 FAIL은 모두 두 필터의 점수가 거의 같아 UNDECIDED로 판정된 사례입니다. 컴퓨터 실수 계산의 미세한 차이를 고려해 epsilon=1e-9보다 작은 차이는 동점으로 처리했습니다. 따라서 정답이 있어도 판정이 동점이면 FAIL입니다.

⑤ 성능과 배운 점

MAC 연산을 100회 반복 측정한 평균을 기록했습니다. N×N 배열에서는 N²개의 위치를 계산하므로 시간 복잡도는 O(N²)입니다. 이번 미션을 통해 이중 반복문, 함수와 클래스, JSON 데이터 처리, 오류 처리, 부동소수점 오차와 성능 분석을 함께 배웠습니다. 무엇보다 결과가 왜 나오는지 이해하는 것이 중요하다고 느꼈습니다. 감사합니다.

### 예상 질문과 답변

| 질문 | 간단한 답변 |
| --- | --- |
| MAC은 무엇인가요? | 같은 위치의 값을 곱하고 모두 더하는 연산입니다. |
| 왜 이중 for문인가요? | 행과 열을 각각 반복하여 2차원 배열의 모든 위치를 방문하기 때문입니다. |
| 함수와 클래스를 왜 썼나요? | 역할별로 나누고 재사용하기 위해서입니다. MiniNPU는 가중치와 편향을 보관합니다. |
| Bias와 ReLU는 무엇인가요? | Bias는 MAC 결과에 더하는 값, ReLU는 음수 결과를 0으로 만드는 활성화 함수입니다. |
| JSON을 왜 사용했나요? | 필터·패턴을 코드와 분리해 저장하고 여러 케이스를 자동 분석하기 위해서입니다. |
| epsilon은 무엇인가요? | 매우 작은 점수 차이를 동점으로 판단하기 위한 허용오차입니다. |
| FAIL 3개는 버그인가요? | 현재 확인된 세 FAIL은 epsilon 동점 판정 때문입니다. 이 결과만으로 버그라고 할 수 없습니다. |
| O(N²)는 무엇인가요? | N×N 배열의 N²개 위치를 방문해 작업량이 제곱에 비례한다는 뜻입니다. |
| 실제 NPU를 만든 건가요? | 아닙니다. CPU에서 실행하는 파이썬 학습용 시뮬레이터입니다. |
| 가장 크게 배운 점은? | 계산 기능뿐 아니라 입력 검증, 판정 기준, 결과 원인 분석이 중요하다는 점입니다. |

### 발표 직전 확인 체크리스트

- [ ] python3 main.py 실행 시 NPU 최종 연산 결과: 3.0이 나오는가?
- [ ] 모드 1에서 Cross 패턴의 A 점수 5, B 점수 1을 설명할 수 있는가?
- [ ] 모드 2에서 PASS 3 / FAIL 3의 이유를 설명할 수 있는가?
- [ ] epsilon=1e-9와 UNDECIDED의 관계를 설명할 수 있는가?
- [ ] O(N²)가 계산 위치 수의 증가를 의미함을 설명할 수 있는가?
- [ ] 실제 NPU 하드웨어가 아니라 파이썬 시뮬레이터임을 구별할 수 있는가?

한 문장 요약: 이 프로젝트는 2차원 배열의 MAC 연산을 파이썬으로 구현하고, JSON 패턴 분류·오류 검증·성능 측정을 통해 AI 연산의 기본 원리를 학습한 결과물입니다.
